# Incident Analysis & Reporting Dashboard

This project consolidates security alerts and scan outputs from multiple tools into a single summary. It demonstrates how to normalise incident data and visualise it for analysts.

## Features

 - **Data aggregation** – Ingest CSV logs from port scanners, log parsers and threat‑intel feeds.  Basic support for JSON can be added by extending the loader.
 - **Summary statistics** – Compute counts by event type and severity and print a console summary.  Optionally compute daily counts.
 - **Visualisation** – Generate grouped bar charts summarising incidents by type/severity as well as daily summaries when requested.
 - **Drill‑down analysis** – Identify the top IP addresses associated with high severity events via a command‑line flag.
 - **Reporting** – Future work will include HTML/PDF report generation and dashboard export.

## Getting started

1. Install dependencies:

   ```bash
   pip install pandas matplotlib
   ```

2. Run the dashboard script on your data.  The basic invocation produces a summary chart grouped by event type and severity:

   ```bash
   python incident_dashboard.py sample_logs.csv summary.png
   ```

   To generate an additional daily summary chart and list the top 3 IPs with high‑severity events, provide the optional flags:

   ```bash
   python incident_dashboard.py sample_logs.csv summary.png --daily-output daily.png --top-high 3
   ```

   This will produce console summaries, save two charts and list the offending IP addresses.

3. Extend the schema to include your own event types or additional fields such as `user` or `source` for richer analysis.

## Files

- `incident_dashboard.py` – main script with input validation and error handling.
- `sample_logs.csv` – example dataset with simulated incidents.
- `incident_chart.png` – sample output bar chart.
- `test_incident_dashboard.py` – unit tests verifying input validation and summary counts.
- `requirements.txt` – minimal list of Python dependencies.
- `setup.py` – packaging metadata enabling installation via `pip`.
- `Dockerfile` – container specification for running the dashboard in isolation.
- `.github/workflows/python.yml` – CI workflow that runs linting and tests on each commit.

## Roadmap & backlog

This project is intentionally modest in scope but has plenty of room for growth.  Planned enhancements include:

- **Packaging & distribution** – Publish to PyPI and provide a `Dockerfile` so users can run the dashboard via `docker run`.
- **Continuous integration** – Add a GitHub Actions workflow to run unit tests and lint the codebase on every push.
- **Interactive user interface** – Provide a minimal web UI or TUI (text‑based UI) to allow analysts to upload log files and view charts interactively.
- **Streaming & advanced ingestion** – Support reading from log streams (e.g. Kafka or AWS Kinesis) and handle large datasets via chunked processing.
- **Correlated analysis** – Extend the analysis to correlate events over time, link high‑severity alerts to specific IPs or users, and identify trends or anomalies.
- **Report generation** – Export interactive HTML or static PDF reports summarising findings and charts.
- **Alerting integrations** – Send notifications to Slack or email when thresholds (e.g. number of high‑severity incidents) are crossed.

You can track these items in the repository’s Issues and Projects boards.
