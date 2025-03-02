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
    ) -> Optional[int]:
        """Add a new expense to the table."""
        # Data initialization & check:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use ISO format (YYYY-MM-DD).")
            return None

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
            self.conn.commit()
            return cursor.lastrowid

        except sqlite3.Error as err:
            print(f"Error adding expense: {err}")
            return None

    def extract_total_date_range(self) -> Optional[tuple[str, str]]:
        """Extracting the minimum and maximum dates among the logged expenses."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM expenses"
        )
        result = cursor.fetchone()

        if result:
            return result["min_date"], result["max_date"]
        return None

    def extract_existing_category_names(self) -> list[str]:
        """Extracting all the category names."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM categories")
        return sorted(r["name"] for r in cursor.fetchall())

    def fetch_expenses(
        self,
        category_name: Optional[str] = None,
        date_range: Optional[tuple[str, str]] = None,
    ) -> list[tuple]:
        """Fetching expenses from the database. Optional filters of category & date
        can be provided. When neither is provided, all expenses are fetched.
        """
        cursor = self.conn.cursor()
        conditions, params = [], []

        if date_range:
            try:
                datetime.strptime(date_range[0], "%Y-%m-%d")
                datetime.strptime(date_range[1], "%Y-%m-%d")
                conditions.append("date BETWEEN ? AND ?")
                params.extend(date_range)
            except ValueError:
                print("Invalid date format. Please use ISO format (YYYY-MM-DD).")

        if category_name:
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            result = cursor.fetchone()

            if result:
                conditions.append("category_id = ?")
                params.append(result["id"])
            else:
                print(f"Category '{category_name}' was not found.")

        query = "SELECT * FROM expenses"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor.execute(query, params)

        return cursor.fetchall()

    def get_all_expenses(self) -> list:
        """Extract all expenses with category names."""
        expenses = []
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT e.id, e.amount, e.description, e.date, c.name as category
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                ORDER BY e.date DESC
            """)
            expenses = cursor.fetchall()
        except sqlite3.Error as err:
            print(f"Error while getting expenses: {err}")
        return expenses

    def get_expenses_by_category(self) -> list:
        """Get total expenses grouped by categories."""
        expenses = []
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT c.name as category, SUM(e.amount) as total
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                GROUP BY c.name
                ORDER BY total DESC
            """)
            expenses = cursor.fetchall()
        except sqlite3.Error as err:
            print(f"Error while getting expenses by category: {err}")
        return expenses

    def get_expenses_by_date_range(self, start_date: str, end_date: str) -> list:
        """Extracting expenses within a date range. Dates must be in ISO format."""
        expenses = []
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Provide the dates as 'YYYY-MM-DD'.")
            return expenses

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT e.id, e.amount, e.description, e.date, c.name as category
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE e.date BETWEEN ? AND ?
                ORDER BY e.date
                """,
                (start_date, end_date),
            )
            expenses = cursor.fetchall()
        except sqlite3.Error as err:
            print(f"Error while getting expenses by date range: {err}")
        return expenses

    def update_expense(
        self,
        expense_id: int,
        amount: Optional[float] = None,
        description: Optional[str] = None,
        category_name: Optional[str] = None,
        date: Optional[str] = None,
    ) -> bool:
        """Updating an existing expense. Only the provided information is modified.

        Returns
        -------
        boolean defining if the expense was updated.
        """
        if amount is None and description is None and category_name is None:
            print("No information was provided to update the expense.")
            return False

        status = False
        try:
            cursor = self.conn.cursor()

            cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
            expense = cursor.fetchone()

            if not expense:
                print(f"Expense with ID {expense_id} not found.")
                return status

            conditions, params = [], []
            if amount is not None:
                conditions.append("amount = ?")
                params.append(amount)

            if description is not None:
                conditions.append(" description = ?")
                params.append(description)

            if category_name is not None:
                cursor.execute(
                    "SELECT id FROM categories WHERE name = ?", (category_name,)
                )
                result = cursor.fetchone()

                if result:
                    category_id = result["id"]
                else:
                    cursor.execute(
                        "INSERT INTO categories (name) VALUES (?)", (category_name,)
                    )
                    category_id = cursor.lastrowid

                conditions.append("category_id = ?")
                params.append(category_id)

            if date is not None:
                conditions.append("date = ?")
                params.append(date)

            query = "UPDATE expenses SET " + " ".join(conditions) + " WHERE id = ?"
            cursor.execute(query, (*params, expense_id))
            self.conn.commit()
            status = True
        except sqlite3.Error as err:
            print(f"Error while updating an expense: {err}")
        return status

    def delete_expense(self, expense_id: int) -> bool:
        """Deleting an expense by ID. A boolean is returned defining whether the
        expense was deleted.
        """
        status = False
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            self.conn.commit()
            status = cursor.rowcount > 0
        except sqlite3.Error as err:
            print(f"Error while deleting expense: {err}")
        return status

    def close(self) -> None:
        """Closing the database connection."""
        self.conn.close()


if __name__ == '__main__':
    DatabaseManager().extract_existing_category_names()
