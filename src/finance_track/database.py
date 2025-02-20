"""All functions for working with the database."""

import contextlib
import sqlite3
from typing import Any, Generator

DATABASE_PATH = "finances.db"


@contextlib.contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, Any, None]:
    """Get a connection to the SQLite database.

    The function is designed to be used as a context manager. While SQLite already
    allows this behavior, this function allows a simple call without the need to
    specify the database file path.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def initialize_database() -> None:
    """Initialization of the database table when this one does not exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Table for categories:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        # Inserting default categories (if they don't exist):
        for category_name in ("general expense", "income"):
            with contextlib.suppress(sqlite3.IntegrityError):
                cursor.execute(
                    "INSERT INTO categories (name) VALUES (?)", (category_name,)
                )

        # Create the 'expenses' table with a foreign key to 'categories':
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,  -- Store date as ISO format (YYYY-MM-DD)
                description TEXT,
                FOREIGN KEY (category_id) REFERENCE categories (id)
            )
        """)


def add_new_category(category_name: str) -> None:
    """Adding a new category to be used with the expenses."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
            print(f"Category '{category_name}' added successfully.")
        except sqlite3.IntegrityError:
            print(f"Category '{category_name}' already exists.")
