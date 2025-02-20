"""Module for bokeh functions (only plotting)."""

from __future__ import annotations

import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure


def _get_empty_figure() -> figure:
    return figure(title="No Data Available", width=800, height=400)


def create_time_line_chart(data: pd.DataFrame) -> figure:
    """Plotting a line chart showing the total expenses over time."""
    p = _get_empty_figure()
    if not data.empty:
        p.title = "Total Expenses Over Time"
        p.x_axis_label = "Date"
        p.y_axis_label = "Amount"
        p.x_axis_type = "datetime"

        data = data.groupby(data["date"].dt.date).sum().reset_index()
        source = ColumnDataSource(data=data)

        p.line(x="date", y="amount", souce=source, line_width=2, color="blue")
    return p


def create_balance_bar_chart(data: pd.DataFrame) -> figure:
    """Plotting a bar chart comparing income VS expenses per month."""
    p = _get_empty_figure()
    if not data.empty:
        # Grouping data by month as YYYY-MM:
        data["month"] = data["date"].dt.to_period("M").astype(str)
        grouped = (
            data.groupby(["month", data["amount"] < 0])
            .agg(total_amount=("amount", "sum"))
            .reset_index()
        )

        # Separate income (negative amount) and expenses (positive amount):
        grouped["type"] = grouped["amount < 0"].apply(
            lambda x: "Income" if x else "Expense"
        )
        grouped["total_amount"] = grouped["total_amount"].abs()

        pivot = (
            grouped.pivot(index="month", columns="type", values="total_amount")
            .fillna(0)
            .reset_index()
        )
        pivot.columns.name = None

        # Bokeh data & plotting:
        source = ColumnDataSource(pivot)

        p.title = "Income vs. Expenses"
        p.x_axis_label = "Month"
        p.y_axis_label = "Amount"
        p.x_range = pivot["month"]

        p.vbar_stack(
            ["Income", "Expenses"],
            x="month",
            width=0.9,
            color=["green", "red"],
            legend_label=["Income", "Expenses"],
            source=source,
        )

        p.xgrid.grid_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"

    return p
