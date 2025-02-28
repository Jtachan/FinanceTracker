"""Module containing an ExpenseVisualizer that used Bokeh."""

from typing import TYPE_CHECKING

import bokeh.plotting as plt
from bokeh.layouts import gridplot
from bokeh.models import UIElement

if TYPE_CHECKING:
    from finance_track.database import DatabaseManager


class ExpenseVisualizer:
    """Visualizer for the expenses using Bokeh."""
    def __init__(self, db_manager: DatabaseManager):
        """Initializing the visualizer with the database manager."""
        self._db_manager = db_manager

    def create_category_pie_chart(self) -> UIElement: ...

    def create_monthly_trend(self) -> UIElement: ...

    def create_category_bar(self) -> UIElement: ...

    def create_dashboard(self, output_filename: str = "expense_dashboard.html"):
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
