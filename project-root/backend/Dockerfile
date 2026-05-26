# FROM python:3.11-slim

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY ./app ./app

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]




FROM python:3.11-slim

WORKDIR /app

# Install postgres client for psql command
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend app
COPY ./app ./app

# Copy sql scripts
COPY ./sql ./sql

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh

# Strip any CRLF that Windows hosts may have introduced, then make executable.
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# Start application
CMD ["/entrypoint.sh"]