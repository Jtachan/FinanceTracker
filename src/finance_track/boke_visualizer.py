"""Module containing an ExpenseVisualizer that used Bokeh."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Optional

import bokeh.plotting as plt
import pandas as pd
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, UIElement
from bokeh.palettes import Category10

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
            y=0,
            radius=0.4,
            start_angle=0,
            end_angle="angle",
            line_color="white",
            fill_color="color",
            legend_field="category",
            source=source,
        )

        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None

        return p

    def create_monthly_trend(self) -> UIElement: ...

    def create_category_bar(self) -> UIElement: ...

    def create_dashboard(self, output_filename: str = "expense_dashboard.html") -> None:
        """Creation of a complete dashboard with multiple visualizations."""
        pie = self.create_category_pie_chart()
        trend = self.create_monthly_trend()
        bar = self.create_category_bar()

        # Creating a layout:
        if pie and trend and bar:
            plt.output_file(output_filename)
            dashboard = gridplot(
                children=[[pie, bar], [trend, None]], width=600, height=400
            )
            plt.show(dashboard)
        else:
            print("Not enough data to generate visualizations")
