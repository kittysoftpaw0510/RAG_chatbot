# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (for PDF and other requirements)
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Run ingest.py before starting the FastAPI app (exec form)
CMD ["sh", "-c", "python utils/ingest.py --clear-pdf && uvicorn main:app --host 0.0.0.0 --port 8000"]
# CMD ["sh", "-c", "python ingest.py && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4"] # If you use GPU