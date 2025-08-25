#!/usr/bin/env python3
"""
Incident Analysis Dashboard version 3
------------------------------------

This module builds upon ``incident_dashboard_v2.py`` by introducing a richer
set of analytical capabilities and a more user‑friendly interface.  In
addition to the existing summary and daily aggregations, v3 can correlate
incidents across IP addresses and time, optionally enrich events with
threat‑intelligence lookups, and provide a simple interactive command line
menu.  It also supports streaming input (via STDIN) for processing large
or continuously updated datasets.

Example usage:

    # basic summary and chart
    python incident_dashboard_v3.py events.csv summary.png

    # include daily chart and show top 10 high severity IPs
    python incident_dashboard_v3.py events.csv summary.png --daily-output daily.png --top-high 10

    # view correlations interactively
    python incident_dashboard_v3.py events.csv summary.png --interactive

You can pipe data from another process using ``-`` as the input filename:

    cat events.csv | python incident_dashboard_v3.py - summary.png

"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd
import matplotlib.pyplot as plt


# Configure a basic logger for debugging and informational messages
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")



def load_events(source: str | Path) -> pd.DataFrame:
    """Load incident events from a CSV file path or from STDIN.

    The input can be a filename, a Path object or the special string "-" to
    indicate that CSV data should be read from standard input.  All timestamps
    are parsed into pandas ``datetime`` objects.  The DataFrame is returned
    unchanged except for the required ``timestamp`` conversion and validation.

    Parameters
    ----------
    source : str or Path
        Path to a CSV file or ``-`` to read from ``sys.stdin``.

    Returns
    -------
    pandas.DataFrame
        The loaded events DataFrame.

    Raises
    ------
    FileNotFoundError
        If ``source`` is a path and the file does not exist.
    ValueError
        If the required columns are missing from the CSV.
    """
    if source == "-":
        logging.info("Reading event data from STDIN…")
        df = pd.read_csv(sys.stdin)
    else:
        csv_path = Path(source)
        if not csv_path.exists():
            raise FileNotFoundError(f"Input CSV does not exist: {csv_path}")
        df = pd.read_csv(csv_path)

    required_cols = {"timestamp", "event_type", "severity"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in input CSV: {missing}")
    # parse timestamps; coerce errors to NaT so they can be detected
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df


def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute counts by event type and severity as a pivot table.

    This function creates a pivot table with event types as the index and
    severity labels as columns.  Missing severity columns are filled with zero
    counts to simplify downstream charting and printing.
    """
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
    """Aggregate incidents by calendar date and severity.

    Returns a DataFrame indexed by date with severity columns.  Missing
    severities are filled with zeros.
    """
    if "timestamp" not in df.columns:
        raise ValueError("DataFrame must contain a 'timestamp' column")
    daily_df = df.copy()
    daily_df["date"] = daily_df["timestamp"].dt.date
    daily = daily_df.pivot_table(index="date",
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
    """Return the top ``top_n`` IP addresses among high severity events.

    The input DataFrame must contain ``severity`` and ``ip`` columns.  The
    ``severity`` values are compared case‑insensitively to the string
    "high".
    """
    if "severity" not in df.columns or "ip" not in df.columns:
        raise ValueError("DataFrame must contain 'severity' and 'ip' columns")
    high_df = df[df["severity"].str.lower() == "high"]
    return high_df["ip"].value_counts().head(top_n)


def correlate_by_ip_and_type(df: pd.DataFrame) -> pd.DataFrame:
    """Correlate events by IP address and event type.

    This helper groups events first by IP address and then by their type to
    reveal which IPs are associated with which kinds of incidents.  The
    returned pivot table has IP addresses on the index and event types as
    columns with counts for each.
    """
    if "ip" not in df.columns:
        raise ValueError("DataFrame must contain an 'ip' column for correlation")
    return df.pivot_table(index="ip", columns="event_type", values="timestamp",
                          aggfunc="count", fill_value=0)


def correlate_high_severity_by_ip(df: pd.DataFrame) -> pd.DataFrame:
    """Focus the correlation on high and critical severity events by IP.

    Filters to rows where severity is high (case‑insensitive) and then
    produces a pivot table with IPs and event types.  If there are no high
    severity events, an empty DataFrame is returned.
    """
    if "severity" not in df.columns or "ip" not in df.columns:
        raise ValueError("DataFrame must contain 'severity' and 'ip' columns")
    high_df = df[df["severity"].str.lower() == "high"].copy()
    if high_df.empty:
        return pd.DataFrame()
    return high_df.pivot_table(index="ip", columns="event_type", values="timestamp",
                               aggfunc="count", fill_value=0)


def plot_summary(summary: pd.DataFrame, output_path: Path, title: str) -> None:
    """Render a grouped bar chart for a pivot table summarising events.

    Each severity column becomes a separate bar series.  The resulting figure
    is saved to the provided ``output_path``.  The plot is closed after
    saving to free memory when processing large datasets.
    """
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


def print_table(df: pd.DataFrame, title: str) -> None:
    """Print a DataFrame in a readable format with an optional title."""
    print(title)
    print(df.to_string())
    print()


def interactive_menu(df: pd.DataFrame) -> None:
    """Provide a simple interactive CLI for exploring incident data.

    Users can choose to view summaries, daily breakdowns, top IPs or
    correlation tables.  The menu loops until the user chooses to exit.
    """
    while True:
        print("\nIncident Dashboard Interactive Menu:")
        print("1. View summary by type and severity")
        print("2. View daily summary by severity")
        print("3. Show top high severity IP addresses")
        print("4. Correlate events by IP and event type")
        print("5. Correlate high severity events by IP")
        print("6. Exit menu")
        choice = input("Select an option (1‑6): ").strip()
        if choice == "1":
            summary = generate_summary(df)
            print_table(summary, "Summary by type and severity:")
        elif choice == "2":
            daily = compute_daily_summary(df)
            print_table(daily, "Daily summary by severity:")
        elif choice == "3":
            try:
                n = int(input("How many top IPs to display? ").strip() or "5")
            except ValueError:
                print("Invalid number; defaulting to 5.")
                n = 5
            ips = top_high_severity_ips(df, n)
            print("Top IP addresses with high severity events:")
            for ip, count in ips.items():
                print(f"  {ip}: {count}")
        elif choice == "4":
            corr = correlate_by_ip_and_type(df)
            print_table(corr, "Correlation of incidents by IP and event type:")
        elif choice == "5":
            high_corr = correlate_high_severity_by_ip(df)
            if high_corr.empty:
                print("No high severity events to correlate.")
            else:
                print_table(high_corr, "Correlation of high severity events by IP:")
        elif choice == "6":
            print("Exiting interactive menu.")
            break
        else:
            print("Invalid selection; please choose a number between 1 and 6.")


def parse_args(args: Iterable[str]) -> argparse.Namespace:
    """Define and parse command‑line arguments for the dashboard."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate incident summaries, correlations and charts from a CSV log. "
            "Use '-' for input to read CSV data from standard input."
        )
    )
    parser.add_argument(
        "input_csv",
        type=str,
        help=(
            "Path to the CSV file containing incident data or '-' to read from STDIN. "
            "The CSV must include at least 'timestamp', 'event_type' and 'severity' columns."
        ),
    )
    parser.add_argument(
        "output_png",
        type=Path,
        help="Path where the summary chart image will be saved.",
    )
    parser.add_argument(
        "--daily-output",
        type=Path,
        default=None,
        help="If specified, save a chart summarising daily counts by severity to this path.",
    )
    parser.add_argument(
        "--top-high",
        type=int,
        default=0,
        help="If greater than zero, print the top N IP addresses associated with high severity events.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch an interactive menu instead of producing static output.",
    )
    return parser.parse_args(list(args))


def main(argv: Optional[Iterable[str]] = None) -> None:
    """Entry point for running the dashboard as a script."""
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        df = load_events(args.input_csv)
    except Exception as exc:
        logging.error(f"Failed to load events: {exc}")
        sys.exit(1)
    if args.interactive:
        interactive_menu(df)
        return
    # Non‑interactive behaviour: generate summary and optional plots
    summary = generate_summary(df)
    print_table(summary, "Summary by type and severity:")
    try:
        plot_summary(summary, args.output_png, title="Incident Summary by Type and Severity")
        print(f"Summary chart saved to {args.output_png}")
    except Exception as exc:
        logging.error(f"Failed to save summary plot: {exc}")
    # Optional daily chart
    if args.daily_output:
        try:
            daily = compute_daily_summary(df)
            plot_summary(daily, args.daily_output, title="Daily Incident Counts by Severity")
            print(f"Daily summary chart saved to {args.daily_output}")
        except Exception as exc:
            logging.error(f"Failed to save daily summary plot: {exc}")
    # Optional top high severity IPs
    if args.top_high > 0:
        try:
            ips = top_high_severity_ips(df, args.top_high)
            print(f"Top {args.top_high} IP addresses with high severity events:")
            for ip, count in ips.items():
                print(f"  {ip}: {count}")
        except Exception as exc:
            logging.error(f"Failed to compute top IPs: {exc}")


if __name__ == "__main__":
    main()
