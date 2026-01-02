# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY update_firewall.py .

# Set environment variables (these should be overridden at runtime)
ENV HETZNER_API_TOKEN=""
ENV HETZNER_FIREWALL_ID=""
ENV FIREWALL_PORTS="80,443"

# Run the script
CMD ["python", "update_firewall.py"]
