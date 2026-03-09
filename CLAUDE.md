# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python project for experimenting with LangGraph (LangChain's framework for building stateful, multi-actor applications with LLMs).

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

# Run linting/formatting
uv run ruff check .
uv run ruff format .

# Type checking
uv run basedpyright

# Run tests
uv run pytest
uv run pytest path/to/test_file.py::test_name  # single test
```
