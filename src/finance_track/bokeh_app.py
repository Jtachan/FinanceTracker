"""Module containing the Bokeh Application (to be launched with 'bokeh serve')."""

from __future__ import annotations

from datetime import datetime, timedelta

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (
    Button,
    DatePicker,
    Div,
    Panel,
    PreText,
    Select,
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
        self.add_button = Button(label="Add Expense", button_type="seccess")
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
                Panel(
                    child=column(header, expense_form, expense_list),
                    title="Track expenses",
                ),
                Panel(child=visualizations, title="Visualizations"),
            ]
        )

        # Add layout to the current document:
        curdoc().add_root(tabs)
        curdoc().title = "Finance Tracker"

        # Initial data load
        self._refresh_expense_list()
        self._refresh_visualizations()

    def _add_expense(self):
        ...

    def _refresh_expense_list(self): ...

    def _refresh_visualizations(self): ...
