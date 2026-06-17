import json

from dataxplan_mcp import _tools as t
from dataxplan_mcp._tools import ContextInput, TableInfoInput

PLAN = json.dumps([{
    "Plan": {
        "Node Type": "Seq Scan", "Relation Name": "orders",
        "Startup Cost": 0.0, "Total Cost": 35811.0, "Plan Rows": 5,
        "Plan Width": 244, "Actual Startup Time": 0.03,
        "Actual Total Time": 900.0, "Actual Rows": 5, "Actual Loops": 1,
        "Filter": "(status = 'X')", "Rows Removed by Filter": 10000000},
    "Planning Time": 0.4, "Execution Time": 905.0}])

FAST = json.dumps([{
    "Plan": {
        "Node Type": "Index Scan", "Relation Name": "orders",
        "Index Name": "orders_pkey", "Plan Rows": 1, "Plan Width": 244,
        "Total Cost": 8.3, "Actual Startup Time": 0.02, "Actual Total Time": 0.05,
        "Actual Rows": 1, "Actual Loops": 1},
    "Execution Time": 0.08}])


def _ids(payload):
    return {f["id"] for f in payload["findings"]}


def test_analyze_plan():
    r = t.analyze_plan(PLAN)
    assert "summary" in r
    ids = _ids(r)
    assert "seq_scan_hot" in ids and "filter_discard" in ids
    seq = next(f for f in r["findings"] if f["id"] == "seq_scan_hot")
    assert seq["reference"] and seq["suggestion"]


def test_analyze_plan_error_has_hint():
    r = t.analyze_plan("not a plan at all")
    assert "error" in r and "describe_inputs" in r["hint"]


def test_analyze_with_context_sharpens():
    ctx = ContextInput(tables={"orders": TableInfoInput(
        row_count=10_000_000, indexed_columns=["id"])})
    r = t.analyze_plan(PLAN, context=ctx)
    seq = next(f for f in r["findings"] if f["id"] == "seq_scan_hot")
    assert "10,000,000 rows" in seq["detail"]


def test_analyze_accepts_text_format():
    text = ("Seq Scan on orders  (cost=0.00..35811.00 rows=5 width=244) "
            "(actual time=0.030..900.000 rows=5 loops=1)\n"
            "  Rows Removed by Filter: 10000000\n"
            "Execution Time: 905.000 ms\n")
    assert "seq_scan_hot" in _ids(t.analyze_plan(text))


def test_compare_plans():
    r = t.compare_plans(PLAN, FAST)
    assert r["verdict"] == "improved"


def test_plan_tree():
    tree = t.plan_tree(PLAN)
    assert "Seq Scan on orders" in tree


def test_describe_inputs():
    d = t.describe_inputs()
    assert d["findings"] and d["thresholds"] and d["accepted_formats"]
    assert "min_time_ms" in d["thresholds"]


def test_payload_is_json_serializable():
    json.dumps(t.analyze_plan(PLAN))
    json.dumps(t.compare_plans(PLAN, FAST))
    json.dumps(t.describe_inputs())


def test_plan_png():
    png = t.plan_png(PLAN)
    assert isinstance(png, bytes) and png[:4] == b"\x89PNG"
