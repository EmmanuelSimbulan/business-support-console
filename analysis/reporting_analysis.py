"""
Business Support Operations Console — Python analysis layer.

Reproduces the KPI tiles, pivot table, and trend charts shown in the
Reporting & Analytics module of index.html, using the same synthetic
source data. Where the HTML page hardcodes a rollup (the pivot counts,
the on-time rate), this script derives it with pandas instead, and adds
a few cuts that don't fit a single-page console: an overdue-item flag,
a share-of-volume ranking by function, and an occupancy-risk flag by
floor/day.

Outputs (written to analysis/output/):
  - business_support_report.xlsx   KPI summary, task register, pivot,
                                    volume ranking, and occupancy sheets
  - charts/*.png                   matplotlib renders of each chart

Run:
    pip install -r requirements.txt
    python analysis/reporting_analysis.py
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

OUTPUT_DIR = Path(__file__).parent / "output"
CHARTS_DIR = OUTPUT_DIR / "charts"
REFERENCE_DATE = date(2026, 9, 8)  # "Week of Sep 8" — matches the console's exec summary

BRASS = "#B8863B"
BLUE = "#3E5C76"
GOOD = "#3B6E58"
RISK = "#A23B3B"
INK = "#1A1F1C"

# ---------------------------------------------------------------------------
# Source data — copied verbatim from the `tasks`, `barData`, `floorData`,
# `dowData`, and `rates` arrays in index.html, so this script and the console
# are reporting on the same underlying facts.
# ---------------------------------------------------------------------------

TASKS = [
    {"name": "Reconcile Q3 vendor statements", "owner": "Accounting", "priority": "Urgent", "status": "In progress", "due": "2026-09-12", "link": "Reduce reconciliation exceptions"},
    {"name": "Draft monthly close scorecard template", "owner": "Business Support", "priority": "Important", "status": "Done", "due": "2026-09-05", "link": "Standardize monthly close reporting"},
    {"name": "Coordinate desk audit for Floor 14", "owner": "Real Estate", "priority": "Urgent", "status": "In progress", "due": "2026-09-11", "link": "Floor 14 reconfiguration"},
    {"name": "Migrate legacy SOPs into shared workspace", "owner": "Business Support", "priority": "Important", "status": "In progress", "due": "2026-09-18", "link": "Consolidate documentation"},
    {"name": "Validate automated batch import rules", "owner": "Technology", "priority": "Urgent", "status": "Not started", "due": "2026-09-10", "link": "Reduce reconciliation exceptions"},
    {"name": "Confirm AV install schedule", "owner": "Technology", "priority": "Important", "status": "Not started", "due": "2026-09-24", "link": "Floor 14 reconfiguration"},
    {"name": "Build stakeholder scorecard automation", "owner": "Business Support", "priority": "Medium", "status": "In progress", "due": "2026-09-25", "link": "Stakeholder scorecard automation"},
    {"name": "Facilitate cross-team requirements workshop", "owner": "Leadership", "priority": "Important", "status": "Done", "due": "2026-09-03", "link": "Standardize monthly close reporting"},
    {"name": "Update floor plan schematics", "owner": "Facilities", "priority": "Medium", "status": "In progress", "due": "2026-09-14", "link": "Floor 14 reconfiguration"},
    {"name": "Archive superseded documentation versions", "owner": "Business Support", "priority": "Low", "status": "Done", "due": "2026-08-29", "link": "Consolidate documentation"},
    {"name": "UAT: new expense-approval workflow", "owner": "Technology", "priority": "Urgent", "status": "In progress", "due": "2026-09-15", "link": "Reduce reconciliation exceptions"},
    {"name": "Prepare leadership business review deck", "owner": "Business Support", "priority": "Important", "status": "Not started", "due": "2026-09-22", "link": "Overview scorecard"},
    {"name": "Audit access controls on shared workspace", "owner": "Technology", "priority": "Urgent", "status": "Not started", "due": "2026-09-12", "link": "Access control audit"},
    {"name": "Draft SOP for new vendor onboarding", "owner": "Accounting", "priority": "Medium", "status": "In progress", "due": "2026-09-19", "link": "New vendor onboarding SOP"},
    {"name": "Weekly reconciliation exception review", "owner": "Accounting", "priority": "Low", "status": "Done", "due": "2026-09-06", "link": "Reduce reconciliation exceptions"},
    {"name": "Send occupant move-in communications", "owner": "Business Support", "priority": "Medium", "status": "Not started", "due": "2026-11-10", "link": "Floor 14 reconfiguration"},
]

TASK_VOLUME_BY_FUNCTION = [
    {"function": "Accounting", "count": 14},
    {"function": "Business Support", "count": 22},
    {"function": "Technology", "count": 13},
    {"function": "Facilities", "count": 8},
    {"function": "Real Estate", "count": 6},
    {"function": "Leadership", "count": 5},
]

OCCUPANCY_BY_FLOOR = [
    {"floor": "Floor 8", "pct": 64},
    {"floor": "Floor 10", "pct": 78},
    {"floor": "Floor 12", "pct": 71},
    {"floor": "Floor 14", "pct": 52},
]

OCCUPANCY_BY_DAY = [
    {"day": "Mon", "pct": 58},
    {"day": "Tue", "pct": 81},
    {"day": "Wed", "pct": 93},
    {"day": "Thu", "pct": 85},
    {"day": "Fri", "pct": 41},
]

COMPLETION_RATE_TREND = [
    {"week": "Wk1", "on_time_pct": 74},
    {"week": "Wk2", "on_time_pct": 78},
    {"week": "Wk3", "on_time_pct": 81},
    {"week": "Wk4", "on_time_pct": 79},
    {"week": "Wk5", "on_time_pct": 85},
    {"week": "Wk6", "on_time_pct": 83},
    {"week": "Wk7", "on_time_pct": 87},
    {"week": "Wk8", "on_time_pct": 87},
]

OCCUPANCY_RISK_THRESHOLD = 85  # matches the >85% flag called out in the console's workspace lede


@dataclass
class AnalysisResult:
    tasks: pd.DataFrame
    pivot: pd.DataFrame
    overdue: pd.DataFrame
    volume_by_function: pd.DataFrame
    occupancy_floor: pd.DataFrame
    occupancy_day: pd.DataFrame
    completion_trend: pd.DataFrame
    kpi_summary: pd.DataFrame


def load_tasks() -> pd.DataFrame:
    df = pd.DataFrame(TASKS)
    df["due"] = pd.to_datetime(df["due"]).dt.date
    return df


def build_status_priority_pivot(tasks: pd.DataFrame) -> pd.DataFrame:
    status_order = ["Not started", "In progress", "Done"]
    priority_order = ["Urgent", "Important", "Medium", "Low"]
    pivot = pd.crosstab(tasks["status"], tasks["priority"])
    pivot = pivot.reindex(index=status_order, columns=priority_order, fill_value=0)
    pivot["Total"] = pivot.sum(axis=1)
    pivot.loc["Total"] = pivot.sum(axis=0)
    return pivot


def find_overdue_open_items(tasks: pd.DataFrame, as_of: date) -> pd.DataFrame:
    open_mask = tasks["status"] != "Done"
    overdue_mask = tasks["due"] < as_of
    return tasks.loc[open_mask & overdue_mask, ["name", "owner", "priority", "status", "due"]].sort_values("due")


def rank_volume_by_function(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows).sort_values("count", ascending=False).reset_index(drop=True)
    df["share_pct"] = (df["count"] / df["count"].sum() * 100).round(1)
    df["cumulative_share_pct"] = df["share_pct"].cumsum().round(1)
    return df


def flag_occupancy_risk(rows: list[dict], key: str) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["over_threshold"] = df["pct"] >= OCCUPANCY_RISK_THRESHOLD
    return df


def summarize_completion_trend(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["change_pts"] = df["on_time_pct"].diff()
    df["rolling_4wk_avg"] = df["on_time_pct"].rolling(4).mean().round(1)
    return df


def build_kpi_summary(tasks: pd.DataFrame, occ_floor: pd.DataFrame, occ_day: pd.DataFrame, trend: pd.DataFrame) -> pd.DataFrame:
    status_counts = tasks["status"].value_counts()
    on_time_now = trend["on_time_pct"].iloc[-1]
    on_time_prior = trend["on_time_pct"].iloc[-2]
    rows = [
        ("Tasks tracked (active register)", len(tasks)),
        ("Tasks done", int(status_counts.get("Done", 0))),
        ("Tasks in progress", int(status_counts.get("In progress", 0))),
        ("Tasks not started", int(status_counts.get("Not started", 0))),
        ("On-time completion rate, latest week", f"{on_time_now}%"),
        ("On-time completion rate, change vs. prior week", f"{on_time_now - on_time_prior:+d} pts"),
        ("Average occupancy, monitored floors", f"{occ_floor['pct'].mean():.1f}%"),
        ("Peak occupancy day", f"{occ_day.loc[occ_day['pct'].idxmax(), 'day']} ({occ_day['pct'].max()}%)"),
        ("Floors/days at or above risk threshold", int(occ_floor["over_threshold"].sum() if "over_threshold" in occ_floor else 0)
            + int(occ_day["over_threshold"].sum() if "over_threshold" in occ_day else 0)),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value"])


def run_analysis() -> AnalysisResult:
    tasks = load_tasks()
    pivot = build_status_priority_pivot(tasks)
    overdue = find_overdue_open_items(tasks, REFERENCE_DATE)
    volume = rank_volume_by_function(TASK_VOLUME_BY_FUNCTION)
    occ_floor = flag_occupancy_risk(OCCUPANCY_BY_FLOOR, "floor")
    occ_day = flag_occupancy_risk(OCCUPANCY_BY_DAY, "day")
    trend = summarize_completion_trend(COMPLETION_RATE_TREND)
    kpi = build_kpi_summary(tasks, occ_floor, occ_day, trend)
    return AnalysisResult(tasks, pivot, overdue, volume, occ_floor, occ_day, trend, kpi)


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def _style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#D7DBD6")
    ax.spines["bottom"].set_color("#D7DBD6")
    ax.tick_params(colors="#5B625C", labelsize=9)
    ax.set_facecolor("#FFFFFF")


def chart_volume_by_function(volume: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=150)
    fig.patch.set_facecolor("#F0F2F0")
    ax.bar(volume["function"], volume["count"], color=BRASS)
    ax.set_title("Task volume by function — current cycle", fontsize=11, color=INK, loc="left")
    for i, row in volume.iterrows():
        ax.text(i, row["count"] + 0.4, f"{row['count']} ({row['share_pct']}%)", ha="center", fontsize=8, color=INK)
    _style_axes(ax)
    fig.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor())
    plt.close(fig)


def chart_occupancy(occ_floor: pd.DataFrame, occ_day: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.4), dpi=150)
    fig.patch.set_facecolor("#F0F2F0")
    colors_floor = [RISK if v else BLUE for v in occ_floor["over_threshold"]]
    axes[0].bar(occ_floor["floor"], occ_floor["pct"], color=colors_floor)
    axes[0].axhline(OCCUPANCY_RISK_THRESHOLD, color=RISK, linestyle="--", linewidth=1)
    axes[0].set_title("Occupancy by floor", fontsize=10.5, color=INK, loc="left")
    colors_day = [RISK if v else BRASS for v in occ_day["over_threshold"]]
    axes[1].bar(occ_day["day"], occ_day["pct"], color=colors_day)
    axes[1].axhline(OCCUPANCY_RISK_THRESHOLD, color=RISK, linestyle="--", linewidth=1)
    axes[1].set_title("Occupancy by day of week — Floor 12", fontsize=10.5, color=INK, loc="left")
    for ax in axes:
        _style_axes(ax)
        ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor())
    plt.close(fig)


def chart_completion_trend(trend: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 3.2), dpi=150)
    fig.patch.set_facecolor("#F0F2F0")
    ax.plot(trend["week"], trend["on_time_pct"], color=BRASS, marker="o", linewidth=2, label="On-time %")
    ax.plot(trend["week"], trend["rolling_4wk_avg"], color=BLUE, linewidth=1.5, linestyle="--", label="4-week rolling avg")
    ax.fill_between(trend["week"], trend["on_time_pct"], trend["on_time_pct"].min() - 5, color=BRASS, alpha=0.08)
    ax.set_title("On-time completion rate — 8-week trend", fontsize=11, color=INK, loc="left")
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    _style_axes(ax)
    fig.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor())
    plt.close(fig)


def render_charts(result: AnalysisResult) -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    chart_volume_by_function(result.volume_by_function, CHARTS_DIR / "task_volume_by_function.png")
    chart_occupancy(result.occupancy_floor, result.occupancy_day, CHARTS_DIR / "occupancy.png")
    chart_completion_trend(result.completion_trend, CHARTS_DIR / "completion_trend.png")


# ---------------------------------------------------------------------------
# Excel export
# ---------------------------------------------------------------------------

def export_workbook(result: AnalysisResult, out_path: Path) -> None:
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        result.kpi_summary.to_excel(writer, sheet_name="KPI Summary", index=False)
        result.tasks.to_excel(writer, sheet_name="Task Register", index=False)
        result.pivot.to_excel(writer, sheet_name="Status x Priority Pivot")
        result.overdue.to_excel(writer, sheet_name="Overdue Open Items", index=False)
        result.volume_by_function.to_excel(writer, sheet_name="Volume by Function", index=False)
        result.completion_trend.to_excel(writer, sheet_name="Completion Trend", index=False)

    _apply_workbook_styling(out_path)


def _apply_workbook_styling(path: Path) -> None:
    from openpyxl import load_workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    wb = load_workbook(path)
    header_fill = PatternFill("solid", fgColor="1A1F1C")
    header_font = Font(color="F5F1E8", bold=True)
    for ws in wb.worksheets:
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(vertical="center")
        ws.freeze_panes = "A2"
        for column_cells in ws.columns:
            length = max((len(str(c.value)) if c.value is not None else 0) for c in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(length + 2, 10), 48)
    wb.save(path)


# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------

def print_summary(result: AnalysisResult) -> None:
    print("=" * 72)
    print("Business Support Operations Console — Python analysis layer")
    print("=" * 72)
    print(f"\nAs of {REFERENCE_DATE.isoformat()}\n")

    print("KPI summary")
    print("-" * 72)
    print(result.kpi_summary.to_string(index=False))

    print("\nStatus x priority pivot (task register)")
    print("-" * 72)
    print(result.pivot.to_string())

    print("\nOverdue, not-yet-done items")
    print("-" * 72)
    if result.overdue.empty:
        print("None — every open item's due date is still ahead of the reference date.")
    else:
        print(result.overdue.to_string(index=False))

    print("\nTask volume by function (share of total)")
    print("-" * 72)
    print(result.volume_by_function.to_string(index=False))

    print(f"\nOutputs written to: {OUTPUT_DIR.resolve()}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result = run_analysis()
    render_charts(result)
    export_workbook(result, OUTPUT_DIR / "business_support_report.xlsx")
    print_summary(result)


if __name__ == "__main__":
    main()
