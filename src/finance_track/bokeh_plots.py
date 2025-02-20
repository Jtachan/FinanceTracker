"""Module for bokeh functions (only plotting)."""

from __future__ import annotations

import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.palettes import Category10
from bokeh.plotting import figure
from bokeh.transform import cumsum


def _get_empty_figure() -> figure:
    return figure(title="No Data Available", width=800, height=400)


def create_time_line_chart(data: pd.DataFrame) -> figure:
    """Plotting a line chart showing the total expenses over time."""
    if data.empty:
        return _get_empty_figure()

    p = figure(
        title="Total Expenses Over Time",
        x_axis_label="Date",
        y_axis_label="Amount",
        x_axis_type="datetime",
        width=800,
        height=400,
        tools="hover",
        tooltips=[("Date", "@date{%F}"), ("Amount", "@amount")]
    )

    data = data.groupby(data["date"].dt.date).sum().reset_index()
    source = ColumnDataSource(data=data)

    p.line(x="date", y="amount", source=source, line_width=2, color="blue")
    return p


def create_balance_bar_chart(data: pd.DataFrame) -> figure:
    """Plotting a bar chart comparing income VS expenses per month."""
    if data.empty:
        return _get_empty_figure()

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

    p = figure(
        title="Income vs. Expenses",
        x_axis_label="Month",
        y_axis_label="Amount",
        x_range=pivot["month"],
        width=800,
        height=400,
        tools="hover",
        tooltips=[
            ("Month", "@month"),
            ("Income", "@Income"),
            ("Expenses", "@Expenses"),
        ]
    )

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


def create_pie_chart(data: pd.DataFrame) -> figure:
    if data.empty:
        return _get_empty_figure()

    # Filtering out any income:
    expenses = data[data["amount"] > 0]
    if expenses.empty:
        return _get_empty_figure()
    category_totals = (
        expenses.groupby("category_name")["amount"]
        .sum()
        .reset_index(name="total_amount")
    )

    category_totals["angle"] = (
        category_totals["total_amount"]
        / category_totals["total_amount"].sum()
        * 2
        * 3.14159
    )
    num_categories = len(category_totals)
    palette = Category10[max(3, min(num_categories, 10))]
    category_totals["color"] = palette[:num_categories]

    source = ColumnDataSource(category_totals)
    p = figure(
        title="Expense distribution by Category",
        toolbar_location=None,
        tools="hover",
        tooltips="@category_name: @total_amount",
        x_range=(-0.5, 1.0),
    )
    p.wedge(
        x=0,
        y=1,
        radius=0.4,
        start_angle=cumsum("angle", include_zero=True),
        end_angle=cumsum("angle"),
        line_color="white",
        fill_color="color",
        legend_field="category_name",
        source=source,
    )

    p.axis.visible = False
    p.grid.grid_line_color = None
    p.legend.label_text_font_size = "8pt"
    p.legend.location = "center_right"

    return p
