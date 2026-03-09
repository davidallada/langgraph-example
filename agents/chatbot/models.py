"""Data models for the library agent."""

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum


class Genre(str, Enum):
    FICTION = "fiction"
    NON_FICTION = "non-fiction"
    SCIENCE = "science"
    HISTORY = "history"
    FANTASY = "fantasy"
    MYSTERY = "mystery"
    BIOGRAPHY = "biography"
    PROGRAMMING = "programming"
    PHILOSOPHY = "philosophy"
    POETRY = "poetry"


LOAN_PERIOD_DAYS = 14
GRACE_PERIOD_DAYS = 3
DAILY_FEE = 0.25
MAX_FEE_PER_BOOK = 10.00


@dataclass
class Book:
    id: str
    title: str
    author: str
    genre: Genre
    isbn: str
    copies_total: int
    copies_available: int
    description: str

    @property
    def is_available(self) -> bool:
        return self.copies_available > 0


@dataclass
class CheckoutRecord:
    book_id: str
    checkout_date: date
    due_date: date

    @classmethod
    def create(
        cls, book_id: str, checkout_date: date | None = None
    ) -> "CheckoutRecord":
        """Create a checkout record with automatic due date calculation."""
        checkout = checkout_date or date.today()
        return cls(
            book_id=book_id,
            checkout_date=checkout,
            due_date=checkout + timedelta(days=LOAN_PERIOD_DAYS),
        )

    def days_overdue(self, as_of: date | None = None) -> int:
        """Return number of days overdue (0 if not overdue). Excludes grace period."""
        today = as_of or date.today()
        days_past_due = (today - self.due_date).days
        if days_past_due <= GRACE_PERIOD_DAYS:
            return 0
        return days_past_due - GRACE_PERIOD_DAYS

    def late_fee(self, as_of: date | None = None) -> float:
        """Calculate late fee for this checkout."""
        overdue = self.days_overdue(as_of)
        return min(overdue * DAILY_FEE, MAX_FEE_PER_BOOK)


@dataclass
class LibraryUser:
    card_number: str
    name: str
    checked_out: list[CheckoutRecord] = field(default_factory=list)
    max_books: int = 5

    def find_checkout(self, book_id: str) -> CheckoutRecord | None:
        """Find a checkout record by book ID."""
        for record in self.checked_out:
            if record.book_id == book_id:
                return record
        return None

    @property
    def checked_out_book_ids(self) -> list[str]:
        return [r.book_id for r in self.checked_out]
