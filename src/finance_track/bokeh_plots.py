"""Module for bokeh functions (only plotting)."""

from __future__ import annotations

import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure


def create_line_chart(data: pd.DataFrame) -> figure:
    """Creating a line chart showing the total expenses over time."""
    if data.empty:
        return figure(title="No Data Available", width=800, height=400)

    data = data.groupby(data["date"].dt.date).sum().reset_index()
    source = ColumnDataSource(data=data)

    p = figure(
        title="Total Expenses Over Time",
        x_axis_label="Date",
        y_axis_label="Amount",
        x_axis_type="datetime",
        width=800,
        height=400,
    )
    p.line(x="date", y="amount", souce=source, line_width=2, color="blue")
    return p
