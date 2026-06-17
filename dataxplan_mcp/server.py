"""The MCP server: registers the dataxplan tools and runs over stdio.

All tools are pure, read-only computations on the plan the agent supplies; the
server never connects to a database. They are marked with annotations so a
client can present and auto-run them safely.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP, Image
from mcp.types import ToolAnnotations

from . import _tools

mcp = FastMCP("dataxplan")


def _annotations(title: str) -> ToolAnnotations:
    return ToolAnnotations(
        title=title,
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=False,
    )


mcp.tool(annotations=_annotations("Analyse an EXPLAIN plan"))(_tools.analyze_plan)
mcp.tool(annotations=_annotations("Compare two plans (regression)"))(_tools.compare_plans)
mcp.tool(annotations=_annotations("Annotated plan tree"))(_tools.plan_tree)
mcp.tool(annotations=_annotations("Describe the inputs"))(_tools.describe_inputs)


@mcp.tool(annotations=_annotations("Self-time chart (PNG)"))
def plan_chart(plan: str) -> Image:
    """Render the self-time-per-node chart for a plan as a PNG image."""
    return Image(data=_tools.plan_png(plan), format="png")


def main() -> None:
    """Console-script entry point: run the server on stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
