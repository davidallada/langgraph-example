"""Book search subagent — helps users discover and find books."""

from langchain_core.tools import tool

from agents.chatbot.data import CATALOG
from agents.chatbot.models import Genre


@tool
def search_books(query: str, genre: str | None = None) -> str:
    """Search the library catalog by title, author, or keyword.

    Args:
        query: Search term to match against title, author, or description.
        genre: Optional genre filter (fiction, non-fiction, science, history, fantasy,
               mystery, biography, programming, philosophy, poetry).
    """
    query_lower = query.lower()
    results = []

    for book in CATALOG.values():
        if genre:
            try:
                target_genre = Genre(genre.lower())
            except ValueError:
                return f"Unknown genre '{genre}'. Valid genres: {', '.join(g.value for g in Genre)}"
            if book.genre != target_genre:
                continue

        if (
            query_lower in book.title.lower()
            or query_lower in book.author.lower()
            or query_lower in book.description.lower()
        ):
            status = "available" if book.is_available else "all copies checked out"
            results.append(
                f"  [{book.id}] '{book.title}' by {book.author} "
                f"({book.genre.value}) — {status}"
            )

    if not results:
        return (
            f"No books found matching '{query}'"
            + (f" in genre '{genre}'" if genre else "")
            + "."
        )

    return f"Found {len(results)} book(s):\n" + "\n".join(results)


@tool
def get_book_details(book_id: str) -> str:
    """Get full details about a specific book.

    Args:
        book_id: The book ID (e.g. "B001").
    """
    book = CATALOG.get(book_id)
    if not book:
        return f"No book found with ID {book_id}."

    return (
        f"Title: {book.title}\n"
        f"Author: {book.author}\n"
        f"Genre: {book.genre.value}\n"
        f"ISBN: {book.isbn}\n"
        f"Description: {book.description}\n"
        f"Availability: {book.copies_available}/{book.copies_total} copies available"
    )


@tool
def browse_by_genre(genre: str) -> str:
    """Browse all books in a given genre.

    Args:
        genre: The genre to browse (fiction, non-fiction, science, history, fantasy,
               mystery, biography, programming, philosophy, poetry).
    """
    try:
        target_genre = Genre(genre.lower())
    except ValueError:
        return f"Unknown genre '{genre}'. Valid genres: {', '.join(g.value for g in Genre)}"

    results = []
    for book in CATALOG.values():
        if book.genre == target_genre:
            status = "available" if book.is_available else "all copies checked out"
            results.append(f"  [{book.id}] '{book.title}' by {book.author} — {status}")

    if not results:
        return f"No books found in the '{genre}' genre."

    return f"Books in {target_genre.value} ({len(results)}):\n" + "\n".join(results)


@tool
def recommend_books(interest: str) -> str:
    """Recommend books based on a user's described interest or mood.

    Args:
        interest: What the user is interested in (e.g. "something adventurous",
                  "learn about history", "a good mystery").
    """
    interest_lower = interest.lower()

    # Simple keyword-to-genre mapping for recommendations
    genre_hints: dict[str, list[Genre]] = {
        "adventure": [Genre.FANTASY, Genre.FICTION],
        "magic": [Genre.FANTASY],
        "fantasy": [Genre.FANTASY],
        "history": [Genre.HISTORY, Genre.BIOGRAPHY],
        "learn": [Genre.SCIENCE, Genre.PROGRAMMING, Genre.PHILOSOPHY],
        "mystery": [Genre.MYSTERY],
        "thriller": [Genre.MYSTERY],
        "code": [Genre.PROGRAMMING],
        "programming": [Genre.PROGRAMMING],
        "python": [Genre.PROGRAMMING],
        "philosophy": [Genre.PHILOSOPHY],
        "stoic": [Genre.PHILOSOPHY],
        "poem": [Genre.POETRY],
        "poetry": [Genre.POETRY],
        "science": [Genre.SCIENCE],
        "space": [Genre.SCIENCE],
        "life story": [Genre.BIOGRAPHY],
        "biography": [Genre.BIOGRAPHY],
    }

    matched_genres: set[Genre] = set()
    for keyword, genres in genre_hints.items():
        if keyword in interest_lower:
            matched_genres.update(genres)

    # If no genre match, search descriptions
    if not matched_genres:
        results = []
        for book in CATALOG.values():
            if book.is_available and interest_lower in book.description.lower():
                results.append(
                    f"  [{book.id}] '{book.title}' by {book.author} — {book.description[:80]}..."
                )
        if results:
            return "Based on your interest, you might enjoy:\n" + "\n".join(results[:5])
        # Fallback: return a mix of available books
        available = [b for b in CATALOG.values() if b.is_available][:3]
        lines = [
            f"  [{b.id}] '{b.title}' by {b.author} ({b.genre.value})" for b in available
        ]
        return "Here are some popular available books:\n" + "\n".join(lines)

    results = []
    for book in CATALOG.values():
        if book.genre in matched_genres and book.is_available:
            results.append(
                f"  [{book.id}] '{book.title}' by {book.author} — {book.description[:80]}..."
            )

    if not results:
        return f"No available books found matching your interest in '{interest}'."

    return f"Based on your interest in '{interest}', I recommend:\n" + "\n".join(
        results[:5]
    )


@tool
def list_all_books(available_only: bool = False) -> str:
    """List every book in the library catalog, grouped by genre.

    Args:
        available_only: If True, only show books with copies available.
    """
    by_genre: dict[Genre, list[str]] = {}
    for book in CATALOG.values():
        if available_only and not book.is_available:
            continue
        line = f"  [{book.id}] '{book.title}' by {book.author}"
        if not book.is_available:
            line += " [unavailable]"
        by_genre.setdefault(book.genre, []).append(line)

    if not by_genre:
        return "No books found in the catalog."

    sections = []
    for genre in Genre:
        books = by_genre.get(genre)
        if books:
            sections.append(
                f"{genre.value.title()} ({len(books)}):\n" + "\n".join(books)
            )

    total = sum(len(b) for b in by_genre.values())
    header = f"Library Catalog — {total} books"
    if available_only:
        header += " (available only)"
    return header + "\n\n" + "\n\n".join(sections)


search_tools = [
    search_books,
    get_book_details,
    browse_by_genre,
    recommend_books,
    list_all_books,
]

SEARCH_AGENT_SYSTEM_PROMPT = """\
You are the Library Search Assistant, a helpful subagent of the main Library Agent.
Your job is to help patrons discover and find books in the library catalog.

You have tools to:
- Search books by title, author, or keyword
- Get detailed information about a specific book
- Browse books by genre
- Recommend books based on interests or mood
- List all books in the entire catalog (use list_all_books)

When helping users:
- Be enthusiastic about books and reading
- If a search returns no results, suggest broadening the search or trying a different genre
- Always mention the book ID (e.g. B001) so the user can check it out
- Let the user know if a book is unavailable so they aren't disappointed
- When recommending, explain briefly why each book might appeal to them
- If the user asks to see everything or wants an overview, use list_all_books
"""
