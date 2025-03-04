"""Code to create a minimal user interface through the command line interface."""

import sys
from datetime import datetime

from finance_track.bokeh_visualizer import ExpenseVisualizer
from finance_track.database import DatabaseManager


def _print_menu() -> None:
    """Printing the menu options."""
    divider = "=" * 20
    print(
        f"\nExpense Tracker\n{divider}\n"
        "1. Add expense\n"
        "2. View all expenses\n"
        "3. View expenses by category\n"
        "4. Update single expense\n"
        "5. Delete single expense\n"
        "6. Visualize expenses\n"
        f"0. Exit\n{divider}"
    )


def _get_float_input(prompt: str) -> float:
    """Get a correct float input from the user."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")


def _get_date_input(prompt: str) -> str:
    """Obtaining the date."""
    while True:
        date_str = input(f"{prompt} (YYYY-MM-DD, press Enter for today): ")
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
            break

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            continue
        break
    return date_str


class CliFinanceTrack:
    """App to be run within the CLI."""

    def __init__(self):
        """Constructor."""
        self._db = DatabaseManager()
        self._visualizer = ExpenseVisualizer(self._db)
        self._choices = {
            0: self.close,
            1: self._add_expense,
            2: self._view_all_expenses,
            3: self._view_expenses_per_category,
            4: self._update_expense,
            5: self._delete_expense,
            6: self._plot_expenses,
        }

    def _add_expense(self):
        amount = _get_float_input("Enter amount: ")
        description = input("Enter description (optional): ")
        category = input("Enter category: ")
        date = _get_date_input("Enter date")

        expense_id = self._db.add_expense(
            amount=amount, category_name=category, date=date, description=description
        )
        if expense_id:
            print(f"Expense added with ID: {expense_id}")
        else:
            print("Failed to add expense.")

    def _view_all_expenses(self):
        expenses = self._db.get_all_expenses()
        if expenses:
            print(
                f"\nAll expenses:\n{'ID':<3} | {'Date':<12} | {'Amount':<10} | "
                f"{'Category':<15} | {'Description'}"
            )
            print("-" * 70)
            for expense in expenses:
                print(
                    f"{expense['id']:<3} | {expense['date']:<12} | "
                    f"{expense['amount']:<9.2f}€ | {expense['category']:<15} | "
                    f"{expense['description']}"
                )
        else:
            print("No expenses found.")

    def _view_expenses_per_category(self):
        expenses = self._db.get_expenses_by_category()
        if expenses:
            print("\nExpenses by Category:")
            print(f"{'Category':<15} {'Total'}")
            print("-" * 25)

            for expense in expenses:
                print(f"{expense['category']:<15} ${expense['total']:.2f}")
        else:
            print("No expenses found.")

    def _update_expense(self):
        expense_id = input("Enter expense ID to update: ")
        try:
            expense_id = int(expense_id)

            print("Leave blank for no change:")
            amount_str = input("New amount: ")
            amount = float(amount_str) if amount_str else None

            description = input("New description: ")
            description = description if description else None

            category = input("New category: ")
            category = category if category else None

            date = _get_date_input("New date")
            date = date if date else None

            if self._db.update_expense(
                expense_id=expense_id,
                amount=amount,
                description=description,
                category_name=category,
                date=date,
            ):
                print("Expense updated successfully.")
            else:
                print("Failed to update expense.")

        except ValueError:
            print("Invalid expense ID.")

    def _delete_expense(self):
        expense_id = input("Enter expense ID to delete: ")
        try:
            expense_id = int(expense_id)

            if self._db.delete_expense(expense_id):
                print("Expense deleted successfully.")
            else:
                print("Failed to delete expense.")

        except ValueError:
            print("Invalid expense ID.")

    def _plot_expenses(self):
        print("\nGenerating visualizations...")
        self._visualizer.create_dashboard()
        print("Dashboard created and opened in your web browser.")

    def close(self) -> None:
        """Closing the app correctly."""
        self._db.close()
        print("Goodbye!")
        sys.exit(0)

    def run(self) -> None:
        """Main loop to run."""
        while True:
            _print_menu()
            try:
                choice = int(input("Enter your choice: "))
            except ValueError:
                print("Enter a valid choice.")
                continue

            if choice not in self._choices:
                print("Enter a valid choice.")
                continue

            self._choices[choice]()


if __name__ == "__main__":
    CliFinanceTrack().run()
