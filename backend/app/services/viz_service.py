"""
Chooses the most suitable Plotly visualization for a result set using
simple heuristics based on column count/types, then serializes the
figure to JSON for the frontend to render with react-plotly.js.
"""

import pandas as pd
import plotly.express as px
import plotly.io as pio


def _is_datetime_like(series: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    try:
        pd.to_datetime(series.dropna().iloc[:5])
        return True
    except Exception:
        return False


def choose_chart(df: pd.DataFrame):
    """Returns (chart_type, plotly_figure_json | None)."""
    if df.empty:
        return "table", None

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    non_numeric_cols = [c for c in df.columns if c not in numeric_cols]

    # Single scalar value -> just show as table/KPI
    if df.shape == (1, 1):
        return "kpi", None

    # No numeric column to plot -> table
    if not numeric_cols:
        return "table", None

    # Time-series: one datetime-like column + one numeric -> line chart
    for col in non_numeric_cols:
        if _is_datetime_like(df[col]):
            fig = px.line(df, x=col, y=numeric_cols[0], markers=True)
            return "line", pio.to_json(fig)

    # One categorical + one numeric, few categories -> bar chart
    if len(non_numeric_cols) == 1 and len(numeric_cols) >= 1:
        cat_col = non_numeric_cols[0]
        if df[cat_col].nunique() <= 12:
            fig = px.bar(df, x=cat_col, y=numeric_cols[0], text_auto=True)
            return "bar", pio.to_json(fig)
        return "table", None

    # Two categoricals + one numeric -> grouped bar
    if len(non_numeric_cols) == 2 and len(numeric_cols) == 1:
        fig = px.bar(
            df, x=non_numeric_cols[0], y=numeric_cols[0],
            color=non_numeric_cols[1], barmode="group"
        )
        return "grouped_bar", pio.to_json(fig)

    # Fallback: table
    return "table", None
