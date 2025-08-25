#!/usr/bin/env python3
"""
Enhanced incident analysis dashboard.

This version expands on the original proof‑of‑concept by adding a command‑line
interface with optional daily summaries and drill‑down into high‑severity
offending IPs.  It maintains robust input validation and error handling.

Usage:

    python incident_dashboard_v2.py sample_logs.csv summary.png
    python incident_dashboard_v2.py sample_logs.csv summary.png --daily-output daily.png --top-high 5

"""
import sys
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def load_events(csv_path: Path) -> pd.DataFrame:
    """Load the event log CSV into a Pandas DataFrame with parsed timestamps."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV does not exist: {csv_path}")
    df = pd.read_csv(csv_path)
    required_cols = {"timestamp", "event_type", "severity"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in input CSV: {missing}")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df


def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a pivot table counting events by type and severity."""
    summary = df.pivot_table(index="event_type",
                             columns="severity",
                             values="timestamp",
                             aggfunc="count",
                             fill_value=0)
    severities = ["low", "medium", "high"]
    for sev in severities:
        if sev not in summary.columns:
            summary[sev] = 0
    return summary[severities]


def compute_daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate events by calendar date and severity."""
    if "timestamp" not in df.columns:
        raise ValueError("DataFrame must contain a 'timestamp' column")
    df = df.copy()
    df["date"] = df["timestamp"].dt.date
    daily = df.pivot_table(index="date",
                           columns="severity",
                           values="timestamp",
                           aggfunc="count",
                           fill_value=0)
    severities = ["low", "medium", "high"]
    for sev in severities:
        if sev not in daily.columns:
            daily[sev] = 0
    return daily[severities]


def top_high_severity_ips(df: pd.DataFrame, top_n: int = 5) -> pd.Series:
    """Return the top IP addresses among high severity events."""
    if "severity" not in df.columns or "ip" not in df.columns:
        raise ValueError("DataFrame must contain 'severity' and 'ip' columns")
    high_df = df[df["severity"].str.lower() == "high"]
    return high_df["ip"].value_counts().head(top_n)


def plot_summary(summary: pd.DataFrame, output_path: Path, title: str) -> None:
    """Render a grouped bar chart for the given summary DataFrame."""
    plt.figure(figsize=(10, 6))
    import numpy as np
    x = np.arange(len(summary.index))
    width = 0.25
    for i, sev in enumerate(summary.columns):
        plt.bar(x + i * width - width, summary[sev], width=width, label=sev.capitalize())
    plt.xticks(x, summary.index, rotation=30, ha='right')
    plt.ylabel("Number of events")
    plt.title(title)
    plt.legend(title="Severity")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def print_summary(summary: pd.DataFrame) -> None:
    """Print a table of counts by type and severity along with totals."""
    print("Incident counts by type and severity:")
    print(summary.to_string())
    print()
    totals = summary.sum(axis=1).sort_values(ascending=False)
    print("Top event types by total count:")
    for event_type, count in totals.items():
        print(f"  {event_type}: {count}")


def parse_args(args: list[str]) -> argparse.Namespace:
    """Define and parse command‑line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate incident summaries and charts from a CSV log. "
            "By default, a summary chart grouped by event type and severity is produced."
        )
    )
    parser.add_argument("input_csv", type=Path, help="Path to the CSV file containing incident data.")
    parser.add_argument("output_png", type=Path, help="Path where the summary chart image will be saved.")
    parser.add_argument("--daily-output", type=Path, default=None,
                        help="If specified, save a chart summarising daily counts by severity to this path.")
    parser.add_argument("--top-high", type=int, default=0,
                        help="If greater than zero, print the top N IP addresses associated with high severity events.")
    return parser.parse_args(args)


def main() -> None:
    args = parse_args(sys.argv[1:])
    df = load_events(args.input_csv)
    # Summary by type/severity
    summary = generate_summary(df)
    print_summary(summary)
    plot_summary(summary, args.output_png, title="Incident Summary by Type and Severity")
    print(f"Summary chart saved to {args.output_png}")
    # Optional daily summary
    if args.daily_output:
        daily = compute_daily_summary(df)
        plot_summary(daily, args.daily_output, title="Daily Incident Counts by Severity")
        print(f"Daily summary chart saved to {args.daily_output}")
    # Optional high severity IP list
    if args.top_high > 0:
        ips = top_high_severity_ips(df, args.top_high)
        print(f"Top {args.top_high} IP addresses with high severity events:")
        for ip, count in ips.items():
            print(f"  {ip}: {count}")


if __name__ == "__main__":
    main()
