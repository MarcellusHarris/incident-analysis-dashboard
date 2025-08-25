# Incident Analysis & Reporting Dashboard

This project consolidates security alerts and scan outputs from multiple tools into a single summary. It demonstrates how to normalise incident data and visualise it for analysts.

## Features

- **Data aggregation** – Ingest CSV or JSON logs from port scanners, log parsers and threat‑intel feeds.
- **Summary statistics** – Compute counts by event type and severity.
- **Visualisation** – Generate bar charts summarising incidents.
- **Reporting** – Export HTML/PDF reports (future work).

## Getting started

1. Install dependencies:

   ```bash
   pip install pandas matplotlib
   ```

2. Run the dashboard script on your data:

   ```bash
   python incident_dashboard.py sample_logs.csv incident_chart.png
   ```

   This will produce a console summary and save a chart.

3. Extend the schema to include your own event types.

## Files

- `incident_dashboard.py` – main script with input validation and error handling.
- `sample_logs.csv` – example dataset with simulated incidents.
- `test_incident_dashboard.py` – unit tests verifying input validation and summary counts.
- `incident_chart.png` – sample bar chart generated from the dataset.

## Sample output

The following bar chart illustrates a sample incident summary generated from the `sample_logs.csv` dataset:

![Incident Summary Chart](incident_chart.png)

## Roadmap

- [ ] Add HTML/PDF report generation.
- [ ] Support for additional log formats and real‑time ingestion.
- [ ] Slack/email alerts for high‑severity thresholds.
- [ ] Unit tests and continuous integration.
