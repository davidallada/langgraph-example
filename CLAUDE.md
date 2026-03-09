# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python project for experimenting with LangGraph (LangChain's framework for building stateful, multi-actor applications with LLMs). Contains multiple agents that are discoverable via the CLI.

## Agents

- **chatbot** (`agents/chatbot/`) — Library assistant with book checkout, search, and late fee tools. Uses a search subagent internally.
- **sql_explorer** (`agents/sql_explorer/`) — SQL tutor that connects to a Chinook SQLite database via an MCP server. Uses `langchain-mcp-adapters` for MCP integration.

All agents are registered in `langgraph.json` and auto-discovered by the CLI.

## Development Setup

- Python 3.13
- Uses `uv` for package management
- Uses `ruff` for linting and formatting
- Uses `basedpyright` for type checking
- Uses `pytest` for testing
- Dev container with Claude Code extension pre-configured

## Commands

```bash
# Install dependencies
uv sync

# Run the agent CLI (interactive chat with any registered agent)
uv run chat
uv run chat --debug  # with tool call tracing

# Run linting/formatting
uv run ruff check .
uv run ruff format .

# Type checking
uv run basedpyright

# Run tests
uv run pytest
uv run pytest path/to/test_file.py::test_name  # single test
```

## Architecture

- `langgraph.json` — Agent registry. Maps agent names to `module_path:attribute` references.
- `cli.py` — Shared interactive CLI. Discovers agents from `langgraph.json`, supports both sync graph attributes and async factory functions.
- `agents/<name>/graph.py` — Each agent's graph definition. Exports either a compiled `graph` object (sync) or a `make_graph()` async factory.
- Agents with async tools (e.g. MCP) must use async node functions, `AsyncSqliteSaver` for checkpointing, and export an async factory.

See `docs/creating-agents.md` for a guide on adding new agents.
