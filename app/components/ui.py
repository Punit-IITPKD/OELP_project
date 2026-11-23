from __future__ import annotations

import pandas as pd
import streamlit as st


def render_historical_notice(message: str | None = None) -> None:
    detail = message or (
        "Forecasts use only purchase history before September 10, 2010. "
        "This is a fixed historical evaluation snapshot, not a live prediction."
    )
    st.info(detail)


def render_page_intro(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


def gbp(value: float | int | None, decimals: int = 0) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"£{float(value):,.{decimals}f}"


def percent(value: float | int | None, decimals: int = 1) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value) * 100:.{decimals}f}%"


def show_download_csv(label: str, frame: pd.DataFrame, file_name: str) -> None:
    st.download_button(
        label=label,
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name=file_name,
        mime="text/csv",
        width="stretch",
    )
