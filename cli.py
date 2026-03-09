"""CLI for interacting with LangGraph agents."""

import asyncio
import importlib
import inspect
import json
import sys
import uuid
from collections.abc import Callable
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessageChunk, ToolMessage
from langgraph.graph.state import CompiledStateGraph
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

load_dotenv()

console = Console()
debug_mode = False

COMMANDS = {
    "/quit": "Exit the CLI",
    "/clear": "Clear conversation history and start a new thread",
    "/switch": "Switch to a different agent",
    "/history": "Show conversation history",
    "/debug": "Toggle debug mode (show tool call traces)",
    "/help": "Show available commands",
}


def discover_agents(config_path: Path = Path("langgraph.json")) -> dict[str, str]:
    """Read langgraph.json and return {name: module_path:attr} mapping."""
    if not config_path.exists():
        console.print("[red]langgraph.json not found in current directory[/red]")
        sys.exit(1)

    config = json.loads(config_path.read_text())
    graphs = config.get("graphs", {})
    if not graphs:
        console.print("[red]No graphs defined in langgraph.json[/red]")
        sys.exit(1)

    return graphs


def _import_module(graph_ref: str):
    """Import and return the module for a graph reference."""
    module_path, _attr = graph_ref.split(":")
    module_name = module_path.lstrip("./").removesuffix(".py").replace("/", ".")
    return importlib.import_module(module_name)


def load_graph(graph_ref: str) -> CompiledStateGraph:
    """Import and return a compiled graph from a 'module_path:attr' reference.

    Supports both a pre-built graph attribute and an async factory function.
    """
    module = _import_module(graph_ref)
    _, attr = graph_ref.split(":")
    obj = getattr(module, attr)
    if callable(obj) and inspect.iscoroutinefunction(obj):
        return asyncio.run(obj())
    return obj


def load_format_fn(graph_ref: str) -> Callable[[str], str] | None:
    """Try to load a format_user_message function from the same module."""
    module = _import_module(graph_ref)
    return getattr(module, "format_user_message", None)


def select_agent(
    agents: dict[str, str],
) -> tuple[str, CompiledStateGraph, Callable[[str], str] | None]:
    """Prompt user to select an agent. Returns (name, compiled_graph, format_fn)."""
    names = list(agents.keys())

    if len(names) == 1:
        name = names[0]
        console.print(f"[dim]Loading agent:[/dim] [bold cyan]{name}[/bold cyan]")
        return name, load_graph(agents[name]), load_format_fn(agents[name])

    table = Table(title="Available Agents", show_header=True)
    table.add_column("#", style="bold")
    table.add_column("Agent", style="cyan")
    table.add_column("Graph", style="dim")
    for i, (name, ref) in enumerate(agents.items(), 1):
        table.add_row(str(i), name, ref)
    console.print(table)

    while True:
        choice = console.input("\n[bold]Select agent number:[/bold] ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(names):
                name = names[idx]
                console.print(f"\n[dim]Loading:[/dim] [bold cyan]{name}[/bold cyan]")
                return name, load_graph(agents[name]), load_format_fn(agents[name])
        except ValueError:
            if choice in agents:
                return (
                    choice,
                    load_graph(agents[choice]),
                    load_format_fn(agents[choice]),
                )
        console.print("[red]Invalid choice, try again.[/red]")


def show_help() -> None:
    table = Table(title="Commands", show_header=True)
    table.add_column("Command", style="bold cyan")
    table.add_column("Description")
    for cmd, desc in COMMANDS.items():
        table.add_row(cmd, desc)
    console.print(table)


def show_history(messages: list) -> None:
    if not messages:
        console.print("[dim]No messages yet.[/dim]")
        return
    for msg in messages:
        role = msg.get("role", getattr(msg, "type", "unknown"))
        content = msg.get("content", getattr(msg, "content", ""))
        if role == "human":
            console.print(f"[bold green]You:[/bold green] {content}")
        else:
            console.print(Panel(Markdown(content), title="Agent", border_style="cyan"))


def _format_tool_args(tool_calls: list) -> str:
    """Format tool call arguments for debug display."""
    parts = []
    for tc in tool_calls:
        name = tc.get("name", "?")
        args = tc.get("args", {})
        args_str = ", ".join(f"{k}={v!r}" for k, v in args.items())
        parts.append(f"{name}({args_str})")
    return "\n".join(parts)


def stream_response(graph: CompiledStateGraph, messages: list, config: dict) -> str:
    """Stream the graph response, printing tokens as they arrive. Returns full response."""
    return asyncio.run(_astream_response(graph, messages, config))


async def _astream_response(
    graph: CompiledStateGraph, messages: list, config: dict
) -> str:
    """Async implementation of stream_response, needed for graphs with async tools."""
    chunks: list[str] = []

    with Live(
        "", console=console, refresh_per_second=15, vertical_overflow="visible"
    ) as live:
        full_text = ""
        async for event in graph.astream(
            {"messages": messages}, config=config, stream_mode="messages"
        ):
            msg, metadata = event
            node = metadata.get("langgraph_node", "")

            # Debug: show tool calls from the agent
            if (
                debug_mode
                and isinstance(msg, AIMessageChunk)
                and hasattr(msg, "tool_call_chunks")
                and msg.tool_call_chunks
            ):
                for tc in msg.tool_call_chunks:
                    if tc.get("name"):
                        args = tc.get("args", "")
                        live.stop()
                        console.print(
                            f"  [dim yellow]-> {tc['name']}[/dim yellow]"
                            f"[dim]({args})[/dim]"
                        )
                        live.start()

            # Debug: show tool responses
            if debug_mode and isinstance(msg, ToolMessage) and node == "tools":
                content = (
                    msg.content if isinstance(msg.content, str) else str(msg.content)
                )
                # Truncate long tool responses
                display = content[:200] + "..." if len(content) > 200 else content
                live.stop()
                console.print(
                    f"  [dim green]<- {msg.name}:[/dim green] [dim]{display}[/dim]"
                )
                live.start()

            # Show tokens from the agent node
            if isinstance(msg, AIMessageChunk) and msg.content and node == "agent":
                token = (
                    msg.content if isinstance(msg.content, str) else str(msg.content)
                )
                chunks.append(token)
                full_text += token
                live.update(Markdown(full_text))

    response = "".join(chunks)
    if not chunks:
        # Fallback: non-streaming invocation
        result = await graph.ainvoke({"messages": messages}, config=config)
        response = result["messages"][-1].content
        console.print(Markdown(response))

    return response


def chat_loop(
    agent_name: str,
    graph: CompiledStateGraph,
    agents: dict[str, str],
    format_fn: Callable[[str], str] | None = None,
) -> None:
    """Main chat loop."""
    global debug_mode
    messages: list[dict[str, str]] = []
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    debug_label = " | [dim yellow]debug[/dim yellow]" if debug_mode else ""
    console.print(
        Panel(
            f"Chatting with [bold cyan]{agent_name}[/bold cyan]  |  "
            f"Thread: [dim]{thread_id[:8]}...[/dim]{debug_label}\n"
            f"Type [bold]/help[/bold] for commands, [bold]/quit[/bold] to exit.",
            border_style="green",
        )
    )

    while True:
        try:
            user_input = console.input("\n[bold green]You:[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue

        if user_input == "/quit":
            console.print("[dim]Goodbye![/dim]")
            break
        elif user_input == "/clear":
            messages.clear()
            thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}
            console.print(
                f"[dim]Conversation cleared. New thread: {thread_id[:8]}...[/dim]"
            )
            continue
        elif user_input == "/help":
            show_help()
            continue
        elif user_input == "/history":
            show_history(messages)
            continue
        elif user_input == "/debug":
            debug_mode = not debug_mode
            state = "[bold yellow]on[/bold yellow]" if debug_mode else "[dim]off[/dim]"
            console.print(f"Debug mode: {state}")
            continue
        elif user_input == "/switch":
            agent_name, graph, format_fn = select_agent(agents)
            messages.clear()
            thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}
            console.print(
                Panel(
                    f"Switched to [bold cyan]{agent_name}[/bold cyan]",
                    border_style="green",
                )
            )
            continue
        elif user_input.startswith("/"):
            console.print(
                f"[red]Unknown command: {user_input}[/red]. Type /help for commands."
            )
            continue

        # Format the message with user context if the agent provides a formatter
        formatted = format_fn(user_input) if format_fn else user_input
        messages.append({"role": "human", "content": formatted})

        try:
            console.print("[bold cyan]Agent:[/bold cyan]")
            response = stream_response(graph, messages, config)
            messages.append({"role": "assistant", "content": response})
        except KeyboardInterrupt:
            console.print("\n[dim]Response interrupted.[/dim]")
            continue
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            messages.pop()
            continue


def main() -> None:
    global debug_mode
    if "--debug" in sys.argv:
        debug_mode = True
        sys.argv.remove("--debug")

    console.print(
        Panel(
            "[bold]LangGraph CLI[/bold]\nInteract with your agents from the terminal.",
            border_style="blue",
        )
    )
    agents = discover_agents()
    agent_name, graph, format_fn = select_agent(agents)
    chat_loop(agent_name, graph, agents, format_fn)


if __name__ == "__main__":
    main()
