# Minimal Dockerfile for running the incident analysis dashboard
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the necessary files
COPY incident_dashboard_v2.py ./
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Define the entrypoint; arguments will be provided at runtime
ENTRYPOINT ["python", "incident_dashboard_v2.py"]
