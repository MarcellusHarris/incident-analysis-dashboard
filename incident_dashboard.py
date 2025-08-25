#!/usr/bin/env python3
"""
incident_dashboard.py
=====================

This script demonstrates a lightweight incident analysis dashboard.  It
reads a CSV log of security events and produces a bar chart summarising
the number of incidents by type and severity.  The goal of this
example is to illustrate how the proposed **Incident Analysis & Reporting
Dashboard** project could aggregate data and visualise it for analysts.

Usage:

    python incident_dashboard.py sample_logs.csv output_chart.png

The script will load the provided CSV file, compute counts grouped by
`event_type` and `severity`, render a grouped bar chart using
Matplotlib, and save the figure to the specified output path.  It will
also print a textual summary to the console.

Dependencies:
    - pandas
    - matplotlib

These can be installed via pip if not already available:
    pip install pandas matplotlib
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def load_events(csv_path: Path) -> pd.DataFrame:
    """
    Load the event log CSV into a Pandas DataFrame.

    Parameters
    ----------
    csv_path : Path
        Path to the CSV file containing incident data.  The file must have
        at least the columns ``timestamp``, ``event_type``, ``severity``.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with parsed datetime values.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    ValueError
        If required columns are missing from the CSV.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV does not exist: {csv_path}")
    df = pd.read_csv(csv_path)
    required_cols = {"timestamp", "event_type", "severity"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in input CSV: {missing}")
    # Parse timestamps; errors='coerce' will convert invalid dates to NaT
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df


def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a summary table counting incidents by type and severity.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing at least ``event_type`` and ``severity`` columns.

    Returns
    -------
    pandas.DataFrame
        A pivot table where rows are event types, columns are severity
        categories (low/medium/high) and values are counts.  Missing
        combinations are filled with zeroes.
    """
    summary = df.pivot_table(index="event_type",
                             columns="severity",
                             values="timestamp",
                             aggfunc="count",
                             fill_value=0)
    # Ensure consistent column order and include missing severities
    severities = ["low", "medium", "high"]
    for sev in severities:
        if sev not in summary.columns:
            summary[sev] = 0
    summary = summary[severities]
    return summary


def plot_summary(summary: pd.DataFrame, output_path: Path) -> None:
    """Plot a grouped bar chart of the summary and save to output_path."""
    plt.figure(figsize=(10, 6))
    # Generate bar positions
    import numpy as np
    x = np.arange(len(summary.index))
    width = 0.25
    for i, sev in enumerate(summary.columns):
        plt.bar(x + i * width - width, summary[sev], width=width, label=sev.capitalize())
    plt.xticks(x, summary.index, rotation=30, ha='right')
    plt.ylabel("Number of events")
    plt.title("Incident Summary by Type and Severity")
    plt.legend(title="Severity")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def print_summary(summary: pd.DataFrame) -> None:
    """Print a human‑readable summary to stdout."""
    print("Incident counts by type and severity:")
    print(summary.to_string())
    print()
    # Top offenders by count across all severities
    totals = summary.sum(axis=1).sort_values(ascending=False)
    print("Top event types by total count:")
    for event_type, count in totals.items():
        print(f"  {event_type}: {count}")


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python incident_dashboard.py <input_csv> <output_png>")
        sys.exit(1)
    csv_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    df = load_events(csv_path)
    summary = generate_summary(df)
    print_summary(summary)
    plot_summary(summary, output_path)
    print(f"Chart saved to {output_path}")


if __name__ == "__main__":
    main()
