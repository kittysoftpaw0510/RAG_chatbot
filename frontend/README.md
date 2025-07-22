# Frontend Service (Streamlit / Gradio)

This directory contains the frontend UI for the RAG Chatbot Portal. It provides a web-based interface for users and admins to interact with the backend services.

## Local Development (Without Docker)

### 1. Setup

1.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### 2. Environment Variable

The frontend needs to know the URL of the backend. This is configured via the `BACKEND_URL` environment variable.

* **For local development**: Set this variable to point to your locally running backend.
    ```bash
    export BACKEND_URL="[http://127.0.0.1:8000](http://127.0.0.1:8000)"
    ```

### 3. Running the Application

* **For Streamlit**:
    ```bash
    streamlit run Home.py
    ```
    The application will be available at `http://localhost:8501`.

* **For Gradio**:
    ```bash
    python app.py
    ```
    The application will be available at `http://localhost:7860`.

## Connecting to the Backend

The application code (`Home.py` or `app.py`) is designed to read the `BACKEND_URL` from the environment.

```python
import os
BASE_URL = os.getenv("BACKEND_URL", "[http://127.0.0.1:8000](http://127.0.0.1:8000)")