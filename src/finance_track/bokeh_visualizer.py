"""Module containing an ExpenseVisualizer that used Bokeh."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Optional

import bokeh.plotting as plt
import pandas as pd
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, HoverTool, UIElement
from bokeh.palettes import Category10
from bokeh.transform import cumsum

if TYPE_CHECKING:
    from finance_track.database import DatabaseManager


class ExpenseVisualizer:
    """Visualizer for the expenses using Bokeh."""

    def __init__(self, db_manager: DatabaseManager):
        """Initializing the visualizer with the database manager."""
        self._db_manager = db_manager

    def create_category_pie_chart(
        self, title: str = "Expenses by Category"
    ) -> Optional[UIElement]:
        """Pie chart plot with the expenses by categories."""
        expenses_by_category = self._db_manager.get_expenses_by_category()
        if not expenses_by_category:
            return None

        # Converting data into a Pandas DataFrame:
        df = pd.DataFrame(expenses_by_category)
        df.columns = ["category", "amount"]

        # Calculating angles for the pie chart:
        df["angle"] = df["amount"] / df["amount"].sum() * 2 * math.pi
        df["color"] = Category10[10][: len(df)]

        # Adding percentage information:
        df["percentage"] = (df["amount"] / df["amount"].sum() * 100).round(1)

        # Bokeh source & plotting
        source = ColumnDataSource(df)
        p = plt.figure(
            title=title,
            height=400,
            width=600,
            toolbar_location=None,
            tools="hover",
            tooltips="@category: @amount€ (@percentage%)",
        )
        p.wedge(
            x=0,
            y=1,
            radius=0.4,
            start_angle=cumsum("angle", include_zero=True),
            end_angle=cumsum("angle"),
            line_color="white",
            fill_color="color",
            legend_field="category",
            source=source,
        )

        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None

        return p

    def create_monthly_trend(
        self, title: str = "Monthly Spending Trend"
    ) -> Optional[UIElement]:
        """Line chart showing monthly spending trend."""
        expenses = self._db_manager.get_all_expenses()
        if not expenses:
            return None

        # Converting into dataframe:
        df = pd.DataFrame(expenses)
        df.columns = ["id", "amount", "description", "date", "category"]

        # Convert date strings to datetime:
        df["date"] = pd.to_datetime(df["date"])

        # Group by month and sum:
        monthly = df.groupby(pd.Grouper(key="date", freq="ME")).sum().reset_index()
        monthly["month"] = monthly["date"].dt.strftime("%Y-%m")

        # Bokeh source & plotting
        source = ColumnDataSource(monthly)
        p = plt.figure(
            title=title,
            x_range=monthly["month"],
            height=400,
            width=700,
            toolbar_location="above",
            tools="pan,wheel_zoom,box_zoom,reset,save",
        )
        p.line("month", "amount", line_width=3, source=source)
        p.scatter("month", "amount", size=8, source=source)
        p.xaxis.major_label_orientation = math.pi / 4

        # Add a hover tool:
        hover = HoverTool()
        hover.tooltips = [("Month", "@month"), ("Total", "@amount{0,0.00}€")]
        p.add_tools(hover)

        return p

    def create_dashboard(self, output_filename: str = "expense_dashboard.html") -> None:
        """Creation of a complete dashboard with multiple visualizations."""
        pie = self.create_category_pie_chart()
        trend = self.create_monthly_trend()

        # Creating a layout:
        if pie and trend:
            plt.output_file(output_filename)
            dashboard = gridplot(children=[[pie, trend]], width=600, height=400)
            plt.show(dashboard)
        else:
            print("Not enough data to generate visualizations")
