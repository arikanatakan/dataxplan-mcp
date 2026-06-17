"""Tool logic, kept free of the MCP SDK so it can be tested directly.

Each tool calls the dataxplan library on the EXPLAIN plan the agent supplies and
returns its JSON-safe payload (metrics, findings with a suggestion and a source
reference) plus a plain-language summary. The server never connects to a
database: the agent runs EXPLAIN and passes the output here.
"""

from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")

import dataxplan  # noqa: E402
from dataxplan.findings import DEFAULT_THRESHOLDS  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

_HINT = "call describe_inputs for how to produce the plan and the accepted formats"

FINDINGS = {
    "estimate_off": "the actual rows are far from the estimate (the usual root "
                    "cause of a bad plan)",
    "seq_scan_hot": "a sequential scan is a large share of a non-trivial query's time",
    "disk_spill": "a sort or hash spilled to disk (work_mem too small)",
    "filter_discard": "a scan read many rows and kept few (non-sargable or a "
                      "missing index)",
    "nested_loop_blowup": "a nested loop ran its inner side many times and it cost "
                          "real time",
    "index_only_heap_fetches": "an index-only scan still hit the heap (the table "
                               "needs VACUUM)",
    "lossy_bitmap": "a bitmap heap scan went lossy (work_mem too small)",
    "jit_overhead": "JIT compilation was a large share of a short query's time",
}

NOTES = (
    "The findings are documented heuristics, not guarantees, and the analysis is "
    "of the plan you provide: the server does not connect to a database, run your "
    "query or read your schema. Self times for parallel plans are total work "
    "across workers, not wall-clock time. Run EXPLAIN with ANALYZE for timing."
)


class TableInfoInput(BaseModel):
    """Optional catalog facts about one table."""

    row_count: float | None = Field(default=None, description="Approximate row count.")
    indexed_columns: list[str] = Field(
        default_factory=list, description="Columns that appear in some index.")
    analyzed: bool = Field(default=True, description="False if statistics look stale.")


class ContextInput(BaseModel):
    """Optional catalog context that sharpens the findings."""

    tables: dict[str, TableInfoInput] = Field(
        default_factory=dict, description="Table name -> catalog facts.")
    work_mem_mb: float | None = Field(default=None, description="The server's work_mem in MB.")


def _context(context: ContextInput | None):
    if context is None:
        return None
    return {
        "tables": {
            name: {"row_count": t.row_count,
                   "indexed_columns": tuple(t.indexed_columns),
                   "analyzed": t.analyzed}
            for name, t in context.tables.items()
        },
        "work_mem_mb": context.work_mem_mb,
    }


def _payload(result) -> dict:
    out = result.to_dict()
    out["summary"] = result.summary()
    return out


def analyze_plan(plan: str, context: ContextInput | None = None,
                 thresholds: dict[str, float] | None = None) -> dict:
    """Analyse a PostgreSQL EXPLAIN plan: bottlenecks, estimation errors and findings.

    ``plan`` is the output of ``EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) ...`` (text,
    YAML and XML are also accepted). Optional ``context`` (table sizes, indexed
    columns, stale stats) sharpens the findings; ``thresholds`` overrides the rule
    cut-offs (see describe_inputs).
    """
    try:
        report = dataxplan.analyze(plan, _context(context), thresholds=thresholds)
        return _payload(report)
    except (ValueError, TypeError, ImportError) as exc:
        return {"error": str(exc), "hint": _HINT}


def compare_plans(before: str, after: str) -> dict:
    """Compare two plans for regression: timing, plan shape, estimates and findings."""
    try:
        return _payload(dataxplan.compare(before, after))
    except (ValueError, TypeError) as exc:
        return {"error": str(exc), "hint": _HINT}


def plan_tree(plan: str) -> str:
    """The plan as an annotated text tree (self time, rows, flags per node)."""
    try:
        return dataxplan.text_tree(dataxplan.analyze(plan))
    except (ValueError, TypeError) as exc:
        return f"error: {exc}\n({_HINT})"


def describe_inputs() -> dict:
    """How to produce the plan, the accepted formats, the findings and thresholds."""
    return {
        "how_to": "Run EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) <query> and pass "
                  "its output as `plan`. ANALYZE adds the real times and row "
                  "counts (needed for self time and most findings); BUFFERS adds "
                  "the block counts.",
        "accepted_formats": ["JSON (exact)", "text (best-effort)", "YAML", "XML"],
        "findings": FINDINGS,
        "thresholds": DEFAULT_THRESHOLDS,
        "notes": NOTES,
    }


def plan_png(plan: str) -> bytes:
    """Render the self-time-per-node chart as PNG bytes."""
    report = dataxplan.analyze(plan)
    fig = dataxplan.plan_tree_chart(report)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    import matplotlib.pyplot as plt
    plt.close(fig)
    return buffer.getvalue()
