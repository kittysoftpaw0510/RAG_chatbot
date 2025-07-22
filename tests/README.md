# Load Testing

This directory contains scripts to perform load testing on the RAG Chatbot backend using [Locust](https://locust.io/), a powerful open-source load testing tool.

The goal of these tests is to simulate concurrent user activity to measure the performance, reliability, and scalability of the API endpoints under load.

## Scripts

* `setup_test_environment.py`: A utility script to prepare the backend for testing by creating a pool of test users and dummy PDF files.
* `locustfile.py`: The main Locust test script that defines the behavior of simulated users (both regular users and admins).

## How to Run the Load Test

Follow these steps to set up and execute the load test against the backend application.

### Step 1: Prerequisites

1.  **Install Locust**: Make sure Locust is installed in your Python environment.
    ```bash
    pip install locust reportlab
    ```

2.  **Run the Backend**: The backend application must be running and accessible. You can run it locally or via Docker Compose.

### Step 2: Prepare the Test Environment

Before launching the test, you need to populate the backend with test data. The setup script is idempotent, meaning it is safe to run multiple times.

1.  **Configure Admin Credentials**: Open `setup_test_environment.py` and ensure the `ADMIN_USERNAME` and `ADMIN_PASSWORD` variables match the credentials of your running backend.

2.  **Run the Setup Script**: From the `tests/` directory, execute the script:
    ```bash
    python setup_test_environment.py
    ```
    This will create 20 test users (from `testuser1` to `testuser20`) and a `test_pdfs` directory with 10 sample PDF files.

### Step 3: Execute the Load Test

1.  **Start Locust**: From the `tests/` directory, run the `locust` command, pointing it to the test script:
    ```bash
    locust -f locustfile.py
    ```

2.  **Open the Locust Web UI**: Open your web browser and navigate to the URL provided in the terminal, which is typically:
    [http://localhost:8089](http://localhost:8089)

3.  **Configure and Start the Swarm**:
    * **Number of users**: Enter the total number of concurrent users to simulate (e.g., `20`).
    * **Spawn rate**: Enter the number of users to start per second (e.g., `5`).
    * **Host**: Enter the full URL of your running backend application (e.g., `http://localhost:8000`).

    Click the **"Start swarming"** button to begin the test.

### Step 4: Analyze the Results

You can monitor the performance of your application in real-time from the Locust web UI.

* **Statistics Tab**: View key metrics like requests per second (RPS), response times (median, 95th percentile), and the number of failures for each endpoint.
* **Charts Tab**: See live graphs of RPS, response times, and the number of running users. This is useful for identifying performance degradation as the load increases.
* **Failures Tab**: See any exceptions or errors that occurred during the test, which can help pinpoint bugs in the backend.
