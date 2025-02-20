"""All functions for working with the database."""

from __future__ import annotations

import contextlib
import sqlite3
from datetime import datetime
from typing import Any, Generator, Union, Optional

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
                name TEXT UNIQUE NOT NULL
            )
        """)

        # Inserting default categories (if they don't exist):
        for category_name in ("general expense", "income"):
            _add_new_category(cursor, category_name)

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


def _add_new_category(cursor: sqlite3.Cursor, category_name: str) -> None:
    """Adding a new category to be used with the expenses.
    If the category already exists, this is skipped.
    """
    with contextlib.suppress(sqlite3.IntegrityError):
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))


def add_expense(
    category: Union[int, str], amount: float, date: str, description: str = ""
) -> None:
    """Add a new expense to the database.

    Parameters
    ----------
    category : int or str
        Either the category ID or category name that corresponds to the expense.
        If a non-existing category name is provided, a new category is defined.
    amount : float
        Real value and positive of the expense. The value is considered negative
        for incomes at the table.
    date : str
        ISO date (YYYY-MM-DD) of the expense.
    description : str, optional
        Description for the expense.
    """
    # Validating the provided date:
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError as err:
        raise ValueError(
            "Invalid date format. Please use ISO format (YYYY-MM-DD)."
        ) from err

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Resolving the provided category:
        table_key = "name" if isinstance(category, str) else "id"
        cursor.execute(f"SELECT id FROM categories WHERE {table_key} = ?", (category,))
        result = cursor.fetchone()
        if not result:
            if table_key == "name":
                _add_new_category(cursor, category)
                cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
                result = cursor.fetchone()
            else:
                raise ValueError(f"Could not find the category '{category}'.")
        category_name, category_id = result["name"], result["id"]

        # Adding the new expense:
        table_amount = -amount if category_name == "income" else amount
        try:
            cursor.execute(
                "INSERT INTO expenses (amount, date, category_id, description) "
                "VALUES (?, ?, ?, ?)",
                (table_amount, date, category_id, description),
            )
            print(f"Expense added successfully: {description} ({amount}) on {date}")
        except sqlite3.IntegrityError as err:
            print(f"Unable adding expense due to error: {err}")


def extract_total_date_range() -> Optional[tuple[str, str]]:
    """Extracts from the table the total date range among all the entries."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM expenses"
        )
        result = cursor.fetchone()

    if result:
        return result["min_date"], result["max_date"]
    return None


def fetch_expenses(
    category: Optional[Union[str, int]] = None,
    date_range: Optional[tuple[str, str]] = None,
) -> list[tuple]:
    """Fetching expenses from the database.
    Optional filters of category & date can be provided.
    """
    conditions, params = [], []
    if date_range:
        try:
            datetime.strptime(date_range[0], "%Y-%m-%d")
            datetime.strptime(date_range[1], "%Y-%m-%d")
        except ValueError as err:
            raise ValueError(
                "Invalid date format. Please use ISO format (YYYY-MM-DD)."
            ) from err
        conditions.append("date BETWEEN ? AND ?")
        params.extend(date_range)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        if category:
            if isinstance(category, str):
                cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
                res = cursor.fetchone()
                if not res:
                    raise ValueError(f"Category '{category}' does not exist.")
                category_id = res["id"]
            else:
                category_id = category
            conditions.append("category_id = ?")
            params.append(category_id)

        query = "SELECT * FROM expenses"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor.execute(query, params)

    return cursor.fetchall()
