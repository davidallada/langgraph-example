"""Library tools for checking books in/out, viewing checkouts, and calculating late fees."""

from datetime import date

from langchain_core.tools import tool

from agents.chatbot.data import CATALOG, USERS
from agents.chatbot.models import (
    DAILY_FEE,
    GRACE_PERIOD_DAYS,
    MAX_FEE_PER_BOOK,
    CheckoutRecord,
)


@tool
def check_out_book(book_id: str, card_number: str) -> str:
    """Check out a book from the library for a user.

    Args:
        book_id: The book ID (e.g. "B001").
        card_number: The user's library card number (e.g. "LIB-1001").
    """
    user = USERS.get(card_number)
    if not user:
        return f"Error: No user found with card number {card_number}."

    book = CATALOG.get(book_id)
    if not book:
        return f"Error: No book found with ID {book_id}."

    if user.find_checkout(book_id):
        return f"You already have '{book.title}' checked out."

    if len(user.checked_out) >= user.max_books:
        return f"You've reached the maximum of {user.max_books} checked-out books. Please return one first."

    if not book.is_available:
        return f"Sorry, '{book.title}' has no copies available right now."

    book.copies_available -= 1
    record = CheckoutRecord.create(book_id)
    user.checked_out.append(record)
    return (
        f"Success! '{book.title}' by {book.author} is now checked out to {user.name}. "
        f"Due back by {record.due_date.strftime('%B %d, %Y')}. "
        f"({book.copies_available}/{book.copies_total} copies remaining)"
    )


@tool
def check_in_book(book_id: str, card_number: str) -> str:
    """Return a book to the library.

    Args:
        book_id: The book ID (e.g. "B001").
        card_number: The user's library card number (e.g. "LIB-1001").
    """
    user = USERS.get(card_number)
    if not user:
        return f"Error: No user found with card number {card_number}."

    book = CATALOG.get(book_id)
    if not book:
        return f"Error: No book found with ID {book_id}."

    record = user.find_checkout(book_id)
    if not record:
        return f"You don't have '{book.title}' checked out."

    # Calculate any outstanding fee before returning
    fee = record.late_fee()
    user.checked_out.remove(record)
    book.copies_available += 1

    msg = (
        f"'{book.title}' has been returned. Thank you, {user.name}! "
        f"({book.copies_available}/{book.copies_total} copies now available)"
    )
    if fee > 0:
        msg += f"\nNote: A late fee of ${fee:.2f} has been assessed for this book."
    return msg


@tool
def list_checked_out_books(card_number: str) -> str:
    """List all books currently checked out by a user, with due dates.

    Args:
        card_number: The user's library card number (e.g. "LIB-1001").
    """
    user = USERS.get(card_number)
    if not user:
        return f"Error: No user found with card number {card_number}."

    if not user.checked_out:
        return f"{user.name} has no books checked out."

    today = date.today()
    lines = [
        f"{user.name}'s checked-out books ({len(user.checked_out)}/{user.max_books} slots used):"
    ]
    for record in user.checked_out:
        book = CATALOG[record.book_id]
        due_str = record.due_date.strftime("%b %d, %Y")
        days_left = (record.due_date - today).days

        if days_left >= 0:
            status = f"due {due_str} ({days_left} days left)"
        else:
            overdue_days = abs(days_left)
            status = f"OVERDUE by {overdue_days} days (due was {due_str})"

        lines.append(f"  - [{book.id}] '{book.title}' by {book.author} — {status}")

    return "\n".join(lines)


@tool
def calculate_late_fees(card_number: str) -> str:
    """Calculate any outstanding late fees for a patron's checked-out books.

    Fee schedule:
    - $0.25 per day overdue (after a 3-day grace period)
    - Maximum $10.00 per book
    - Books returned on time or within the grace period incur no fee

    Args:
        card_number: The user's library card number (e.g. "LIB-1001").
    """
    user = USERS.get(card_number)
    if not user:
        return f"Error: No user found with card number {card_number}."

    if not user.checked_out:
        return f"{user.name} has no books checked out, so no fees to calculate."

    today = date.today()
    total_fees = 0.0
    lines = [f"Late fee report for {user.name} (as of {today.strftime('%B %d, %Y')}):"]
    lines.append(
        f"Fee schedule: ${DAILY_FEE:.2f}/day after {GRACE_PERIOD_DAYS}-day grace period "
        f"(max ${MAX_FEE_PER_BOOK:.2f}/book)"
    )
    lines.append("")

    has_fees = False
    for record in user.checked_out:
        book = CATALOG[record.book_id]
        fee = record.late_fee(today)
        overdue = record.days_overdue(today)
        days_past = (today - record.due_date).days

        if days_past <= 0:
            # Not yet due
            lines.append(
                f"  [{book.id}] '{book.title}' — on time (due {record.due_date.strftime('%b %d')})"
            )
        elif overdue == 0:
            # Past due but within grace period
            lines.append(
                f"  [{book.id}] '{book.title}' — {days_past} day(s) past due "
                f"(within {GRACE_PERIOD_DAYS}-day grace period, no fee)"
            )
        else:
            # Overdue with fees
            has_fees = True
            total_fees += fee
            capped = " (CAPPED)" if fee >= MAX_FEE_PER_BOOK else ""
            lines.append(
                f"  [{book.id}] '{book.title}' — {days_past} days past due, "
                f"{overdue} billable days = ${fee:.2f}{capped}"
            )

    lines.append("")
    if has_fees:
        lines.append(f"Total outstanding fees: ${total_fees:.2f}")
    else:
        lines.append(
            "No outstanding fees. All books are on time or within the grace period."
        )

    return "\n".join(lines)
