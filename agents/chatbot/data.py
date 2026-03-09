"""Test data for the library agent — book catalog and sample users."""

from datetime import date, timedelta

from agents.chatbot.models import Book, CheckoutRecord, Genre, LibraryUser

today = date.today()

CATALOG: dict[str, Book] = {}
USERS: dict[str, LibraryUser] = {}


def _add_book(book: Book) -> None:
    CATALOG[book.id] = book


def _add_user(user: LibraryUser) -> None:
    USERS[user.card_number] = user


# ── Fiction ──────────────────────────────────────────────────────────────────

_add_book(
    Book(
        id="B001",
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        genre=Genre.FICTION,
        isbn="978-0-7432-7356-5",
        copies_total=3,
        copies_available=2,
        description="A story of the mysteriously wealthy Jay Gatsby and his love for Daisy Buchanan in 1920s Long Island.",
    )
)
_add_book(
    Book(
        id="B013",
        title="To Kill a Mockingbird",
        author="Harper Lee",
        genre=Genre.FICTION,
        isbn="978-0-06-112008-4",
        copies_total=4,
        copies_available=3,
        description="A young girl in Depression-era Alabama witnesses her father defend a Black man accused of a terrible crime.",
    )
)
_add_book(
    Book(
        id="B014",
        title="1984",
        author="George Orwell",
        genre=Genre.FICTION,
        isbn="978-0-451-52493-5",
        copies_total=3,
        copies_available=1,
        description="A dystopian novel about totalitarian surveillance, thought control, and the struggle for individual freedom.",
    )
)
_add_book(
    Book(
        id="B015",
        title="Pride and Prejudice",
        author="Jane Austen",
        genre=Genre.FICTION,
        isbn="978-0-14-143951-8",
        copies_total=3,
        copies_available=3,
        description="The witty and romantic tale of Elizabeth Bennet and Mr. Darcy navigating class, family, and love.",
    )
)
_add_book(
    Book(
        id="B016",
        title="The Catcher in the Rye",
        author="J.D. Salinger",
        genre=Genre.FICTION,
        isbn="978-0-316-76948-0",
        copies_total=2,
        copies_available=2,
        description="Holden Caulfield narrates his disillusioned wanderings through New York City after being expelled from school.",
    )
)
_add_book(
    Book(
        id="B017",
        title="One Hundred Years of Solitude",
        author="Gabriel Garcia Marquez",
        genre=Genre.FICTION,
        isbn="978-0-06-088328-7",
        copies_total=2,
        copies_available=1,
        description="The multi-generational saga of the Buendia family in the mythical town of Macondo.",
    )
)

# ── Science ──────────────────────────────────────────────────────────────────

_add_book(
    Book(
        id="B002",
        title="A Brief History of Time",
        author="Stephen Hawking",
        genre=Genre.SCIENCE,
        isbn="978-0-553-38016-3",
        copies_total=2,
        copies_available=2,
        description="An exploration of cosmology: the Big Bang, black holes, and the nature of time itself.",
    )
)
_add_book(
    Book(
        id="B018",
        title="The Selfish Gene",
        author="Richard Dawkins",
        genre=Genre.SCIENCE,
        isbn="978-0-19-857519-1",
        copies_total=2,
        copies_available=2,
        description="A groundbreaking look at evolution from the gene's perspective, introducing the concept of memes.",
    )
)
_add_book(
    Book(
        id="B019",
        title="Cosmos",
        author="Carl Sagan",
        genre=Genre.SCIENCE,
        isbn="978-0-345-53943-4",
        copies_total=3,
        copies_available=3,
        description="A sweeping tour of the universe exploring stars, galaxies, and humanity's place in the cosmos.",
    )
)
_add_book(
    Book(
        id="B020",
        title="The Structure of Scientific Revolutions",
        author="Thomas S. Kuhn",
        genre=Genre.SCIENCE,
        isbn="978-0-226-45812-0",
        copies_total=2,
        copies_available=1,
        description="A landmark work on how scientific paradigms shift and revolutionize our understanding of the world.",
    )
)

# ── Fantasy ──────────────────────────────────────────────────────────────────

_add_book(
    Book(
        id="B003",
        title="The Name of the Wind",
        author="Patrick Rothfuss",
        genre=Genre.FANTASY,
        isbn="978-0-7564-0407-9",
        copies_total=4,
        copies_available=3,
        description="The tale of Kvothe, a legendary figure told from his own perspective in a fantasy world.",
    )
)
_add_book(
    Book(
        id="B009",
        title="The Hobbit",
        author="J.R.R. Tolkien",
        genre=Genre.FANTASY,
        isbn="978-0-547-92822-7",
        copies_total=5,
        copies_available=4,
        description="Bilbo Baggins embarks on an unexpected journey with dwarves to reclaim a lost kingdom.",
    )
)
_add_book(
    Book(
        id="B021",
        title="A Game of Thrones",
        author="George R.R. Martin",
        genre=Genre.FANTASY,
        isbn="978-0-553-10354-0",
        copies_total=4,
        copies_available=2,
        description="Noble families vie for control of the Iron Throne in a sprawling epic of politics, war, and magic.",
    )
)
_add_book(
    Book(
        id="B022",
        title="The Way of Kings",
        author="Brandon Sanderson",
        genre=Genre.FANTASY,
        isbn="978-0-7653-2635-5",
        copies_total=3,
        copies_available=3,
        description="An epic fantasy set on Roshar, a world of storms, where ancient powers are reawakening.",
    )
)
_add_book(
    Book(
        id="B023",
        title="The Fellowship of the Ring",
        author="J.R.R. Tolkien",
        genre=Genre.FANTASY,
        isbn="978-0-547-92821-0",
        copies_total=4,
        copies_available=3,
        description="Frodo Baggins begins his quest to destroy the One Ring and save Middle-earth from the Dark Lord Sauron.",
    )
)

# ── History ──────────────────────────────────────────────────────────────────

_add_book(
    Book(
        id="B004",
        title="Sapiens: A Brief History of Humankind",
        author="Yuval Noah Harari",
        genre=Genre.HISTORY,
        isbn="978-0-06-231609-7",
        copies_total=3,
        copies_available=1,
        description="A sweeping narrative of human history from the Stone Age to the Silicon Age.",
    )
)
_add_book(
    Book(
        id="B024",
        title="Guns, Germs, and Steel",
        author="Jared Diamond",
        genre=Genre.HISTORY,
        isbn="978-0-393-31755-8",
        copies_total=3,
        copies_available=2,
        description="Why did some civilizations conquer others? A study of geography, agriculture, and the fate of societies.",
    )
)
_add_book(
    Book(
        id="B025",
        title="The Silk Roads",
        author="Peter Frankopan",
        genre=Genre.HISTORY,
        isbn="978-1-101-91237-9",
        copies_total=2,
        copies_available=2,
        description="A new history of the world told through the ancient trade routes connecting East and West.",
    )
)

# ── Mystery ──────────────────────────────────────────────────────────────────

_add_book(
    Book(
        id="B005",
        title="Murder on the Orient Express",
        author="Agatha Christie",
        genre=Genre.MYSTERY,
        isbn="978-0-06-269366-2",
        copies_total=2,
        copies_available=2,
        description="Detective Hercule Poirot investigates a murder aboard the famous Orient Express train.",
    )
)
_add_book(
    Book(
        id="B012",
        title="Gone Girl",
        author="Gillian Flynn",
        genre=Genre.MYSTERY,
        isbn="978-0-307-58836-4",
        copies_total=3,
        copies_available=3,
        description="A twisting thriller about the disappearance of Amy Dunne on her fifth wedding anniversary.",
    )
)
_add_book(
    Book(
        id="B026",
        title="The Girl with the Dragon Tattoo",
        author="Stieg Larsson",
        genre=Genre.MYSTERY,
        isbn="978-0-307-45440-8",
        copies_total=3,
        copies_available=2,
        description="A journalist and a brilliant hacker investigate a decades-old disappearance in Sweden.",
    )
)
_add_book(
    Book(
        id="B027",
        title="And Then There Were None",
        author="Agatha Christie",
        genre=Genre.MYSTERY,
        isbn="978-0-06-227376-5",
        copies_total=2,
        copies_available=1,
        description="Ten strangers are lured to an island where they are killed one by one according to a nursery rhyme.",
    )
)
_add_book(
    Book(
        id="B028",
        title="The Da Vinci Code",
        author="Dan Brown",
        genre=Genre.MYSTERY,
        isbn="978-0-307-47427-7",
        copies_total=3,
        copies_available=3,
        description="A symbologist uncovers a conspiracy hidden in Leonardo da Vinci's artwork that threatens the Catholic Church.",
    )
)

# ── Biography ────────────────────────────────────────────────────────────────

_add_book(
    Book(
        id="B006",
        title="Steve Jobs",
        author="Walter Isaacson",
        genre=Genre.BIOGRAPHY,
        isbn="978-1-4516-4853-9",
        copies_total=2,
        copies_available=0,
        description="The definitive biography of Apple co-founder Steve Jobs, based on extensive interviews.",
    )
)
_add_book(
    Book(
        id="B029",
        title="The Autobiography of Malcolm X",
        author="Malcolm X and Alex Haley",
        genre=Genre.BIOGRAPHY,
        isbn="978-0-345-35068-8",
        copies_total=2,
        copies_available=2,
        description="The powerful life story of Malcolm X, from his troubled youth to his emergence as a civil rights leader.",
    )
)
_add_book(
    Book(
        id="B030",
        title="Einstein: His Life and Universe",
        author="Walter Isaacson",
        genre=Genre.BIOGRAPHY,
        isbn="978-0-7432-6473-0",
        copies_total=2,
        copies_available=1,
        description="A comprehensive biography of Albert Einstein exploring the man behind the genius and his revolutionary ideas.",
    )
)
_add_book(
    Book(
        id="B031",
        title="Becoming",
        author="Michelle Obama",
        genre=Genre.BIOGRAPHY,
        isbn="978-1-5247-6313-8",
        copies_total=3,
        copies_available=2,
        description="The former First Lady's intimate memoir, from childhood in Chicago to life in the White House.",
    )
)

# ── Programming ──────────────────────────────────────────────────────────────

_add_book(
    Book(
        id="B007",
        title="Design Patterns",
        author="Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
        genre=Genre.PROGRAMMING,
        isbn="978-0-201-63361-0",
        copies_total=3,
        copies_available=3,
        description="The classic 'Gang of Four' guide to reusable object-oriented software design patterns.",
    )
)
_add_book(
    Book(
        id="B010",
        title="Fluent Python",
        author="Luciano Ramalho",
        genre=Genre.PROGRAMMING,
        isbn="978-1-492-05635-5",
        copies_total=2,
        copies_available=1,
        description="A hands-on guide to writing effective, idiomatic Python code.",
    )
)
_add_book(
    Book(
        id="B032",
        title="Clean Code",
        author="Robert C. Martin",
        genre=Genre.PROGRAMMING,
        isbn="978-0-13-235088-4",
        copies_total=3,
        copies_available=2,
        description="A handbook of agile software craftsmanship focused on writing readable, maintainable code.",
    )
)
_add_book(
    Book(
        id="B033",
        title="The Pragmatic Programmer",
        author="David Thomas and Andrew Hunt",
        genre=Genre.PROGRAMMING,
        isbn="978-0-13-595705-9",
        copies_total=2,
        copies_available=2,
        description="Timeless lessons on software development covering everything from career advice to coding techniques.",
    )
)
_add_book(
    Book(
        id="B034",
        title="Introduction to Algorithms",
        author="Thomas H. Cormen et al.",
        genre=Genre.PROGRAMMING,
        isbn="978-0-262-04630-5",
        copies_total=3,
        copies_available=1,
        description="The comprehensive textbook on algorithms, covering sorting, graph theory, dynamic programming, and more.",
    )
)
_add_book(
    Book(
        id="B035",
        title="Structure and Interpretation of Computer Programs",
        author="Harold Abelson and Gerald Jay Sussman",
        genre=Genre.PROGRAMMING,
        isbn="978-0-262-51087-5",
        copies_total=2,
        copies_available=2,
        description="A foundational CS text using Scheme to teach abstraction, recursion, and metalinguistic design.",
    )
)

# ── Philosophy ───────────────────────────────────────────────────────────────

_add_book(
    Book(
        id="B008",
        title="Meditations",
        author="Marcus Aurelius",
        genre=Genre.PHILOSOPHY,
        isbn="978-0-14-044933-4",
        copies_total=2,
        copies_available=2,
        description="Personal writings of the Roman Emperor on Stoic philosophy and self-improvement.",
    )
)
_add_book(
    Book(
        id="B036",
        title="Thus Spoke Zarathustra",
        author="Friedrich Nietzsche",
        genre=Genre.PHILOSOPHY,
        isbn="978-0-14-044118-5",
        copies_total=2,
        copies_available=2,
        description="A philosophical novel exploring the Ubermensch, eternal recurrence, and the death of God.",
    )
)
_add_book(
    Book(
        id="B037",
        title="The Republic",
        author="Plato",
        genre=Genre.PHILOSOPHY,
        isbn="978-0-14-044914-3",
        copies_total=3,
        copies_available=3,
        description="Plato's foundational dialogue on justice, the ideal state, and the nature of the philosopher-king.",
    )
)
_add_book(
    Book(
        id="B038",
        title="Being and Time",
        author="Martin Heidegger",
        genre=Genre.PHILOSOPHY,
        isbn="978-0-06-157559-4",
        copies_total=1,
        copies_available=0,
        description="A dense exploration of the question of Being and human existence as Dasein.",
    )
)

# ── Poetry ───────────────────────────────────────────────────────────────────

_add_book(
    Book(
        id="B011",
        title="The Collected Poems of Emily Dickinson",
        author="Emily Dickinson",
        genre=Genre.POETRY,
        isbn="978-1-59308-050-3",
        copies_total=2,
        copies_available=2,
        description="The complete collection of Emily Dickinson's profound and innovative poetry.",
    )
)
_add_book(
    Book(
        id="B039",
        title="Leaves of Grass",
        author="Walt Whitman",
        genre=Genre.POETRY,
        isbn="978-0-14-042199-6",
        copies_total=2,
        copies_available=2,
        description="Whitman's landmark poetry collection celebrating democracy, nature, love, and the human body.",
    )
)
_add_book(
    Book(
        id="B040",
        title="The Waste Land and Other Poems",
        author="T.S. Eliot",
        genre=Genre.POETRY,
        isbn="978-0-451-52684-7",
        copies_total=2,
        copies_available=1,
        description="Eliot's modernist masterpiece exploring post-war disillusionment, myth, and cultural fragmentation.",
    )
)

# ── Non-Fiction ──────────────────────────────────────────────────────────────

_add_book(
    Book(
        id="B041",
        title="Thinking, Fast and Slow",
        author="Daniel Kahneman",
        genre=Genre.NON_FICTION,
        isbn="978-0-374-27563-1",
        copies_total=3,
        copies_available=2,
        description="A Nobel laureate explains the two systems that drive how we think: fast intuition and slow reasoning.",
    )
)
_add_book(
    Book(
        id="B042",
        title="The Lean Startup",
        author="Eric Ries",
        genre=Genre.NON_FICTION,
        isbn="978-0-307-88789-4",
        copies_total=2,
        copies_available=2,
        description="A methodology for developing businesses and products through validated learning and rapid experimentation.",
    )
)
_add_book(
    Book(
        id="B043",
        title="Quiet: The Power of Introverts",
        author="Susan Cain",
        genre=Genre.NON_FICTION,
        isbn="978-0-307-35214-9",
        copies_total=2,
        copies_available=1,
        description="How introverts are undervalued in a culture that rewards extroversion, and why that needs to change.",
    )
)
_add_book(
    Book(
        id="B044",
        title="Atomic Habits",
        author="James Clear",
        genre=Genre.NON_FICTION,
        isbn="978-0-7352-1129-2",
        copies_total=4,
        copies_available=3,
        description="A practical guide to building good habits and breaking bad ones through tiny changes that compound.",
    )
)

# ── Users ────────────────────────────────────────────────────────────────────

_add_user(
    LibraryUser(
        card_number="LIB-1001",
        name="Alice Johnson",
        checked_out=[
            # Gatsby: checked out 30 days ago, due 16 days ago → overdue (past grace period, ~$3.25)
            CheckoutRecord(
                book_id="B001",
                checkout_date=today - timedelta(days=30),
                due_date=today - timedelta(days=16),
            ),
            # Sapiens: checked out 10 days ago, due in 4 days → on time
            CheckoutRecord(
                book_id="B004",
                checkout_date=today - timedelta(days=10),
                due_date=today + timedelta(days=4),
            ),
            # 1984: checked out 16 days ago, due 2 days ago → within 3-day grace period (no fee)
            CheckoutRecord(
                book_id="B014",
                checkout_date=today - timedelta(days=16),
                due_date=today - timedelta(days=2),
            ),
        ],
    )
)
_add_user(
    LibraryUser(
        card_number="LIB-1002",
        name="Bob Smith",
        checked_out=[
            # Steve Jobs: checked out 60 days ago, way overdue → capped at $10
            CheckoutRecord(
                book_id="B006",
                checkout_date=today - timedelta(days=60),
                due_date=today - timedelta(days=46),
            ),
            # Name of the Wind: checked out 5 days ago → on time
            CheckoutRecord(
                book_id="B003",
                checkout_date=today - timedelta(days=5),
                due_date=today + timedelta(days=9),
            ),
        ],
    )
)
_add_user(
    LibraryUser(
        card_number="LIB-1003",
        name="Charlie Park",
        checked_out=[],
    )
)

# Default user for quick testing
DEFAULT_USER = USERS["LIB-1001"]
