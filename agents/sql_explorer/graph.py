"""SQL Explorer agent — uses an MCP SQLite server to query the Chinook database."""

from pathlib import Path

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.store.memory import InMemoryStore

load_dotenv()

# ── Config ───────────────────────────────────────────────────────────────────

DB_PATH = str(Path(__file__).parent / "chinook.db")

SYSTEM_PROMPT = """\
You are an SQL tutor helping a student practice SQL queries on the Chinook database \
(a digital music store).

The database contains these tables:
- Artist (ArtistId, Name)
- Album (AlbumId, Title, ArtistId)
- Track (TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice)
- Genre (GenreId, Name)
- MediaType (MediaTypeId, Name)
- Playlist (PlaylistId, Name)
- PlaylistTrack (PlaylistId, TrackId)
- Customer (CustomerId, FirstName, LastName, Company, Address, City, State, Country, PostalCode, Phone, Fax, Email, SupportRepId)
- Employee (EmployeeId, LastName, FirstName, Title, ReportsTo, BirthDate, HireDate, Address, City, State, Country, PostalCode, Phone, Fax, Email)
- Invoice (InvoiceId, CustomerId, InvoiceDate, BillingAddress, BillingCity, BillingState, BillingCountry, BillingPostalCode, Total)
- InvoiceLine (InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity)

Guidelines:
- When a student asks a question, first run the query yourself using the tools to verify the answer.
- Explain the query and results clearly.
- If the student asks you to write a query, show it and run it so they can see the output.
- Encourage the student to try writing queries themselves.
- If a query has errors, explain what went wrong and suggest corrections.
- For complex questions, break the query down step by step.
- IMPORTANT: Only use SELECT queries. Never modify the database.
"""

# ── LLM ──────────────────────────────────────────────────────────────────────

model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

# ── Graph (async factory — MCP client setup requires async) ──────────────────


async def make_graph():
    """Build the SQL explorer graph with MCP tools loaded from the SQLite server."""
    client = MultiServerMCPClient(
        {
            "sqlite": {
                "command": "uvx",
                "args": ["mcp-server-sqlite", "--db-path", DB_PATH],
                "transport": "stdio",
            },
        }
    )

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

    # Checkpointer & store
    checkpointer = MemorySaver()
    store = InMemoryStore()

    return builder.compile(checkpointer=checkpointer, store=store)
