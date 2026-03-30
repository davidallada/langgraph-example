# Creating a New Agent

This guide walks through adding a new agent to the project. Every agent lives under `agents/<name>/` and is registered in `langgraph.json` so the CLI can discover it.

## Project Structure

```
agents/
  chatbot/           # Library assistant (sync graph)
    graph.py         # Exports `graph` (compiled StateGraph)
    tools.py         # Tool functions
    ...
  sql_explorer/      # SQL tutor with MCP (async graph)
    graph.py         # Exports `make_graph()` async factory
    chinook.db       # Bundled SQLite database
langgraph.json       # Agent registry
cli.py               # Shared interactive CLI
```

## Step 1: Create the Agent Directory

```bash
mkdir -p agents/my_agent
touch agents/my_agent/__init__.py
```

## Step 2: Define the Graph

Create `agents/my_agent/graph.py`. There are two patterns depending on whether your agent uses async tools.

### Pattern A: Sync Graph (simple tools)

Use this when all your tools are regular Python functions.

```python
"""My agent description."""

import sqlite3

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

model = ChatAnthropic(model="claude-sonnet-4-6")

# ── Tools ────────────────────────────────────────────────────────────────────

@tool
def my_tool(query: str) -> str:
    """Description of what this tool does."""
    return f"Result for {query}"

tools = [my_tool]

# ── System prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = "You are a helpful assistant."

# ── Graph ────────────────────────────────────────────────────────────────────

def agent_node(state: MessagesState) -> MessagesState:
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    response = model.bind_tools(tools).invoke(messages)
    return {"messages": [response]}

builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

db_conn = sqlite3.connect("my_agent_checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(db_conn)

graph = builder.compile(checkpointer=checkpointer)
```

**Key:** Export a `graph` variable (the compiled `CompiledStateGraph`).

### Pattern B: Async Factory (MCP or async tools)

Use this when your tools come from an MCP server or are otherwise async.

```python
"""My async agent description."""

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.store.memory import InMemoryStore

load_dotenv()

model = ChatAnthropic(model="claude-sonnet-4-6")

SYSTEM_PROMPT = "You are a helpful assistant."

async def make_graph():
    """Async factory — called once at startup."""
    # Connect to MCP server(s)
    client = MultiServerMCPClient({
        "my_server": {
            "command": "uvx",
            "args": ["my-mcp-server", "--some-flag"],
            "transport": "stdio",
        },
    })

    tools = await client.get_tools()
    llm_with_tools = model.bind_tools(tools)

    async def agent_node(state: MessagesState) -> MessagesState:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *state["messages"]]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    checkpointer = AsyncSqliteSaver.from_conn_string("my_agent_checkpoints.db")
    store = InMemoryStore()

    return builder.compile(checkpointer=checkpointer, store=store)
```

**Key differences from sync:**
- Export an `async def make_graph()` function instead of a `graph` variable
- Use `async def` for node functions and `ainvoke` for LLM calls
- Use `AsyncSqliteSaver` instead of `SqliteSaver` (requires `aiosqlite`)
- MCP tools are loaded inside the factory since `get_tools()` is async

## Step 3: Register in langgraph.json

Add your agent to the `graphs` mapping:

```json
{
  "dependencies": ["."],
  "graphs": {
    "chatbot": "./agents/chatbot/graph.py:graph",
    "sql_explorer": "./agents/sql_explorer/graph.py:make_graph",
    "my_agent": "./agents/my_agent/graph.py:graph"
  },
  "env": ".env"
}
```

The value format is `./path/to/graph.py:attribute_name`. For async factories, point to the function name (e.g., `make_graph`).

## Step 4: Optional — User Message Formatting

If your agent needs context injected into every user message (like the chatbot adds patron name/card number), export a `format_user_message` function from your `graph.py`:

```python
def format_user_message(query: str) -> str:
    """Called by the CLI before sending each user message to the agent."""
    return f"[Context: some useful info]\n{query}"
```

The CLI auto-detects this function and applies it. If not present, user messages are passed through as-is.

## How the Pieces Fit Together

### The Graph

LangGraph graphs are state machines. The standard agent loop is:

```
START -> agent node -> (has tool calls?) -> tools node -> agent node -> ... -> END
```

- **Agent node**: Calls the LLM with the system prompt and conversation history. The LLM decides whether to call a tool or respond directly.
- **Tools node**: `ToolNode` executes whatever tool(s) the LLM requested and returns the results.
- **`tools_condition`**: Built-in routing function that checks if the LLM's response contains tool calls. Routes to the tools node if yes, END if no.

### Checkpointer

Persists conversation state across turns. Each conversation gets a `thread_id` so multiple independent conversations can run. The CLI generates a new `thread_id` on startup and when you `/clear`.

- `SqliteSaver` — for sync graphs
- `AsyncSqliteSaver` — for async graphs (MCP, etc.)

### MCP Integration

[MCP (Model Context Protocol)](https://modelcontextprotocol.io/) lets you connect to external tool servers. The `langchain-mcp-adapters` package bridges MCP servers into LangChain-compatible tools.

`MultiServerMCPClient` manages one or more MCP server connections. Supported transports:

| Transport | Use case | Config |
|-----------|----------|--------|
| `stdio` | Local process (most common) | `command`, `args` |
| `http` | Remote HTTP server | `url`, optional `headers` |
| `sse` | Server-Sent Events | `url` |

### The CLI

`cli.py` provides a shared interactive chat interface. It:

1. Reads `langgraph.json` to discover all agents
2. Loads the selected agent's graph (handling both sync attributes and async factories)
3. Optionally loads a `format_user_message` function from the agent module
4. Runs an interactive chat loop with streaming, debug mode, and conversation management

CLI commands:
- `/quit` — exit
- `/clear` — reset conversation
- `/switch` — change to a different agent
- `/history` — show conversation history
- `/debug` — toggle tool call tracing
- `/help` — show commands

## Checklist

When creating a new agent, make sure you:

- [ ] Created `agents/<name>/__init__.py` and `agents/<name>/graph.py`
- [ ] Exported either a `graph` object (sync) or `make_graph()` function (async)
- [ ] Added the agent to `langgraph.json`
- [ ] Used `AsyncSqliteSaver` if your graph has async nodes/tools
- [ ] Ran `uv run ruff check .` and `uv run ruff format .`
- [ ] Tested with `uv run chat`
