"""Library agent — a user-facing agent for a library with tools and a book search subagent."""

import sqlite3

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool as make_tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, create_react_agent, tools_condition
from langgraph.store.memory import InMemoryStore

from agents.chatbot.data import DEFAULT_USER
from agents.chatbot.search_agent import (
    SEARCH_AGENT_SYSTEM_PROMPT,
    search_tools,
)
from agents.chatbot.tools import (
    calculate_late_fees,
    check_in_book,
    check_out_book,
    list_checked_out_books,
)

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────

model = ChatOpenAI(model="gpt-4o-mini")

# ── Search subagent (wrapped as a tool) ──────────────────────────────────────

search_agent = create_react_agent(
    model=model,
    tools=search_tools,
    prompt=SEARCH_AGENT_SYSTEM_PROMPT,
)


def _call_search_agent(query: str) -> str:
    """Delegate to the book search subagent."""
    result = search_agent.invoke({"messages": [("human", query)]})
    return result["messages"][-1].content


@make_tool
def find_books(query: str) -> str:
    """Search, browse, or get book recommendations from the library catalog.

    Use this when a patron wants to:
    - Search for a book by title, author, or keyword
    - Browse books in a genre
    - Get recommendations based on their interests
    - Look up details about a specific book

    Args:
        query: The user's search query or description of what they're looking for.
    """
    return _call_search_agent(query)


# ── All tools available to the main agent ────────────────────────────────────

library_tools = [
    check_out_book,
    check_in_book,
    list_checked_out_books,
    calculate_late_fees,
    find_books,
]

# ── Prompts ──────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are the Library Assistant at Greenfield Public Library. You help patrons manage their \
library account and discover books.

You have the following capabilities:
1. **Check out books** — use the check_out_book tool with the book ID and patron's card number
2. **Return books** — use the check_in_book tool with the book ID and patron's card number
3. **View checked-out books** — use the list_checked_out_books tool with the patron's card number
4. **Check late fees** — use the calculate_late_fees tool with the patron's card number \
to see any outstanding fees, overdue books, and the fee breakdown
5. **Find books** — use the find_books tool to search, browse, or get recommendations \
(this delegates to a specialized search assistant)

Important guidelines:
- Always greet the patron by name when starting a conversation
- When a patron wants to check out a book but doesn't know the ID, use find_books first
- Always confirm the action after checking out or returning a book
- If a book is unavailable, suggest similar alternatives using find_books
- Be warm, helpful, and enthusiastic about reading
- You already know the patron's identity from their library card — don't ask for it again
- When using tools, pass the patron's card number automatically — don't ask them for it
"""

USER_PROMPT_TEMPLATE = """\
[Library Patron Context]
Name: {name}
Library Card: {card_number}

{query}\
"""

# ── Graph ────────────────────────────────────────────────────────────────────


def build_system_message() -> SystemMessage:
    return SystemMessage(content=SYSTEM_PROMPT)


def agent_node(state: MessagesState) -> MessagesState:
    """Call the LLM with tools bound."""
    messages = [build_system_message(), *state["messages"]]
    response = model.bind_tools(library_tools).invoke(messages)
    return {"messages": [response]}


# Build the graph
builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(library_tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

# ── Checkpointer & Store ────────────────────────────────────────────────────

db_conn = sqlite3.connect("library_checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(db_conn)
store = InMemoryStore()

graph = builder.compile(checkpointer=checkpointer, store=store)

# ── Helper for CLI integration ───────────────────────────────────────────────

DEFAULT_CARD_NUMBER = DEFAULT_USER.card_number
DEFAULT_NAME = DEFAULT_USER.name


def format_user_message(
    query: str, name: str = DEFAULT_NAME, card_number: str = DEFAULT_CARD_NUMBER
) -> str:
    """Format a user query with the patron context template."""
    return USER_PROMPT_TEMPLATE.format(name=name, card_number=card_number, query=query)
