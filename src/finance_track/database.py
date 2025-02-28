"""Manager to work with the database."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Optional

DEFAULT_CATEGORIES = [
    "Food",
    "Transportation",
    "Housing",
    "Entertainment",
    "Utilities",
    "Other",
]


class DatabaseManager:
    """Instance to work directly with the database."""

    def __init__(self, db_file: str = "finances.db"):
        """Initialization of the database."""
        self._db_file = db_file

        # Connecting to the SQLite database:
        try:
            self.conn: sqlite3.Connection = sqlite3.connect(self._db_file)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as err:
            raise RuntimeError("Database connection error") from err

    def create_tables(self) -> None:
        """Creation of the necessary tables if they don't exist."""
        cursor = self.conn.cursor()

        # Creating the categories table:
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            # Create the expenses table:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    description TEXT,
                    date TEXT NOT NULL,  -- Date in ISO format
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            """)

            # Inserting default categories:
            for category in DEFAULT_CATEGORIES:
                cursor.execute(
                    "INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,)
                )
            self.conn.commit()
        except sqlite3.Error as err:
            raise RuntimeError("Table creation error") from err

    def add_expense(
        self,
        amount: float,
        category_name: str,
        date: Optional[str] = None,
        description: str = "",
    ) -> None:
        """Add a new expense to the table."""
        # Data initialization & check:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use ISO format (YYYY-MM-DD).")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            result = cursor.fetchone()

            if result:
                category_id = result["id"]
            else:
                # Insert new category:
                cursor.execute(
                    "INSERT INTO categories (name) VALUES (?)", (category_name,)
                )
                category_id = cursor.lastrowid

            # Insert expense:
            cursor.execute(
                "INSERT INTO expenses (amount, description, date, category_id) "
                "VALUES (?, ?, ?, ?)",
                (amount, description, date, category_id),
            )

        except sqlite3.Error as err:
            print(f"Error adding expense: {err}")
