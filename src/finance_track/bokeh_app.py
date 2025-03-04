"""Module containing the Bokeh Application (to be launched with 'bokeh serve')."""

from __future__ import annotations

from datetime import datetime, timedelta

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (
    Button,
    DatePicker,
    Div,
    PreText,
    Select,
    TabPanel,
    Tabs,
    TextInput,
)

from finance_track.bokeh_visualizer import ExpenseVisualizer
from finance_track.database import DatabaseManager


class FinanceTrackerApp:
    """Bokeh application for the finance tracker."""

    def __init__(self):
        """Constructor of the app. No parameters are required."""
        self._db_manager = DatabaseManager()
        self._visualizer = ExpenseVisualizer(self._db_manager)

        # -----------
        # Main header
        # -----------
        header = Div(
            text="""
            <h1 style="text-align:center; color:#2F4F4F">Finance Tracker</h1>
            <p style="text align:center">Track and visualize your finances</p>
            """,
            width=800,
        )

        # ------------------------
        # Form to add new expenses
        # ------------------------

        # Input components:
        self.amount_input = TextInput(title="Amount (€)", placeholder="Enter amount...")
        self.description_input = TextInput(
            title="Description", placeholder="Enter description..."
        )

        # Categories extracted from the database:
        categories = self._db_manager.extract_existing_category_names()
        self.category_select = Select(
            title="Category", options=categories, value=categories[0]
        )

        # Date picker with today set as default.
        # Allows selecting dates from two years past until today.
        today = datetime.now().date()
        self.date_picker = DatePicker(
            title="Date",
            value=today,
            min_date=today - timedelta(days=365 * 2),
            max_date=today,
        )

        # Button to add the expense:
        self.add_button = Button(label="Add entry", button_type="success")
        self.add_button.on_click(self._add_expense)
        self.status_message = Div(text="", width=400)

        expense_form = column(
            Div(text="<h3>Add New Expense</h3>", width=400),
            row(self.amount_input, self.category_select, width=600),
            row(self.description_input, self.date_picker, width=600),
            row(self.add_button, width=200),
            self.status_message,
            width=800,
        )

        # ---------------------
        # Expenses table & list
        # ---------------------
        self.expense_table = PreText(text="", width=800)
        self.refresh_button = Button(label="Refresh list", button_type="primary")
        self.refresh_button.on_click(self._refresh_expense_list)

        expense_list = column(
            Div(text="<h3>Recent Expenses</h3>", width=800),
            self.refresh_button,
            self.expense_table,
            width=800,
        )

        # --------------
        # Visualizations
        # --------------
        self.viz_refresh_button = Button(
            label="Refresh visualizations", button_type="primary"
        )
        self.viz_refresh_button.on_click(self._refresh_visualizations)

        # Containers
        self.pie_chart_container = column(width=600, height=500)
        self.trend_chart_container = column(width=600, height=500)

        visualizations = column(
            Div(text="<h3>Expense visualizations</h3>", width=800),
            self.viz_refresh_button,
            row(self.pie_chart_container, self.trend_chart_container),
            width=1200,
        )

        # ----------------------------------------
        # Conjoining the Tabs for all the sections
        # ----------------------------------------
        tabs = Tabs(
            tabs=[
                TabPanel(
                    child=column(header, expense_form, expense_list),
                    title="Track expenses",
                ),
                TabPanel(child=visualizations, title="Visualizations"),
            ]
        )

        # Add layout to the current document:
        curdoc().add_root(tabs)
        curdoc().title = "Finance Tracker"

        # Initial data load
        self._refresh_expense_list()
        self._refresh_visualizations()

    def _add_expense(self) -> None:
        """Adding a new expense into the database."""
        try:
            amount = float(self.amount_input.value)
            description = self.description_input.value
            category = self.category_select.value
            date = self.date_picker.value

            expense_id = self._db_manager.add_expense(
                amount=amount,
                category_name=category,
                date=date,
                description=description,
            )
            if expense_id:
                msg = "<p style='color:green'>Entry added!</p>"
                # Clear form and refreshing values:
                self.amount_input.value = ""
                self.description_input.value = ""
                self._refresh_expense_list()
                self._refresh_visualizations()
            else:
                msg = "<p style='color:red'>Failed to add entry</p>"
        except BaseException:  # noqa: BLE001
            msg = "<p style='color:red'>Failed to add entry</p>"
        self.status_message.text = msg

    def _refresh_expense_list(self):
        """Refresh the expense list display."""
        expenses = self._db_manager.get_all_expenses()

        if expenses:
            header = (
                f"{'ID':<5}{'Date':<12}{'Category':<15}{'Amount':<10}"
                f"{'Description':<30}"
            )
            separator = "-" * 72
            rows = [header, separator]

            # Displaying the last 20 entries:
            for expense in expenses[:20]:
                exp_row = (
                    f"{expense['id']:<5}{expense['date']:<12}"
                    f"{expense['category']:<15}{expense['amount']:<10.2f}"
                    f"{expense['description']:<30}"
                )
                rows.append(exp_row)

            if len(expenses) > 20:
                rows.append(
                    "Displaying only the 20 last entries. Use visualizations "
                    "to see all data."
                )
            self.expense_table.text = "\n".join(rows)

        else:
            self.expense_table.text = "No expenses found."

    def _refresh_visualizations(self):
        """Refresh the visualization displays."""
        self.pie_chart_container.children = []
        self.trend_chart_container.children = []

        if pie_chart := self._visualizer.create_category_pie_chart():
            self.pie_chart_container.children = [pie_chart]
        else:
            self.pie_chart_container.children = [
                Div(text="<p>Not enough data for category chart</p>")
            ]

        if trend_chart := self._visualizer.create_monthly_trend():
            self.trend_chart_container.children = [trend_chart]
        else:
            self.trend_chart_container.children = [
                Div(text="<p>Not enough data for trend chart</p>")
            ]


app = FinanceTrackerApp()
