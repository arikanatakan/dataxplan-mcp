# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project uses
[semantic versioning](https://semver.org/).

## [0.1.0] - 2026-06-17

First release.

### Added

- Tools wrapping dataxplan: `analyze_plan` (metrics, findings with a suggestion
  and a source reference), `compare_plans` (regression), `plan_tree` (annotated
  text tree), `plan_chart` (a self-time PNG) and `describe_inputs`.
- stdio server built on FastMCP, with read-only tool annotations. The server
  never connects to a database; the agent runs EXPLAIN and passes the output.
