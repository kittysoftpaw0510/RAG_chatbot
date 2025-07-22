# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the frontend application files into the container at /app
COPY . .

# Expose the port that Streamlit runs on
EXPOSE 8501

# Define a healthcheck to make sure the container is running
HEALTHCHECK CMD streamlit hello

# Run the Streamlit app when the container launches
# The --server.address=0.0.0.0 is crucial to allow traffic from outside the container
# The --server.enableCORS=false is often needed when running behind a reverse proxy or in Docker Compose
CMD ["streamlit", "run", "home.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false"]
