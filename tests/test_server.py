def test_server_imports_and_wires():
    from dataxplan_mcp import server

    assert server.mcp is not None
    assert callable(server.main)


def test_all_tools_registered():
    import asyncio

    from dataxplan_mcp import server

    names = {tool.name for tool in asyncio.run(server.mcp.list_tools())}
    expected = {
        "analyze_plan", "compare_plans", "plan_tree", "describe_inputs",
        "plan_chart",
    }
    assert expected <= names
