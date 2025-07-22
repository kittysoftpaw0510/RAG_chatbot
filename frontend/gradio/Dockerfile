# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
# Make sure you have a requirements.txt file in the same directory
# It should contain: gradio, requests, pandas
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the Gradio application files into the container at /app
COPY . .

# Expose the port that Gradio runs on by default
EXPOSE 7860

# Run the Gradio app when the container launches
# The --server-name=0.0.0.0 is crucial to allow traffic from outside the container
CMD ["python", "app.py", "--server-name", "0.0.0.0"]
