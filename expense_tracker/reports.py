"""Summaries with pandas and charts with Matplotlib."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw straight to files; no window is needed
import matplotlib.pyplot as plt
import pandas as pd

from .database import Expense

COLUMNS = ["id", "date", "amount", "category", "description"]


def to_dataframe(expenses: list[Expense]) -> pd.DataFrame:
    """Turns a list of expenses into a DataFrame with a proper datetime column."""
    df = pd.DataFrame([vars(e) for e in expenses], columns=COLUMNS)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    return df


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Total, count and average spending per month (YYYY-MM)."""
    if df.empty:
        return pd.DataFrame(columns=["month", "total", "count", "average"])
    out = (df.assign(month=df["date"].dt.strftime("%Y-%m"))
             .groupby("month")["amount"]
             .agg(total="sum", count="count", average="mean")
             .reset_index())
    out[["total", "average"]] = out[["total", "average"]].round(2)
    return out


def category_summary(df: pd.DataFrame, month: str | None = None) -> pd.DataFrame:
    """Total per category, biggest first, with each category's share of the total in percent.
    Pass month='2026-10' to look at a single month."""
    if month:
        df = df[df["date"].dt.strftime("%Y-%m") == month]
    if df.empty:
        return pd.DataFrame(columns=["category", "total", "percent"])
    out = (df.groupby("category")["amount"].sum()
             .sort_values(ascending=False)
             .reset_index(name="total"))
    out["percent"] = (out["total"] / out["total"].sum() * 100).round(1)
    out["total"] = out["total"].round(2)
    return out


def save_charts(df: pd.DataFrame, folder: str | Path = "charts") -> list[Path]:
    """Saves a monthly bar chart and a category pie chart as PNG files and returns their paths."""
    if df.empty:
        return []
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    monthly = monthly_summary(df)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(monthly["month"], monthly["total"], color="#4C72B0")
    ax.set_title("Spending per month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total spent")
    fig.tight_layout()
    bar_path = folder / "monthly_spending.png"
    fig.savefig(bar_path)
    plt.close(fig)

    cats = category_summary(df)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(cats["total"], labels=cats["category"], autopct="%1.1f%%", startangle=90)
    ax.set_title("Spending by category")
    pie_path = folder / "category_breakdown.png"
    fig.savefig(pie_path)
    plt.close(fig)
    return [bar_path, pie_path]
