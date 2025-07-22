# RAG Chatbot Portal

This project is a full-stack web application that provides an admin and user portal for a Retrieval-Augmented Generation (RAG) chatbot. It consists of a FastAPI backend for API services and a choice of a Streamlit or Gradio frontend for the user interface.

The entire application is designed to be containerized with Docker and deployed to cloud platforms like Google Cloud Platform (GCP).

## Project Structure

```
.
├── backend/
│   ├── Dockerfile
│   ├── README.md
│   └── ... (FastAPI source code)
│
├── frontend/ (or frontend-gradio/)
│   ├── Dockerfile
│   ├── README.md
│   └── ... (Streamlit/Gradio source code)
│
├── tests/
│   ├── locustfile.py
│   ├── setup_test_environment.py
│   └── ... (Load testing scripts)
│
└── docker-compose.yml
```

## Features

* **Dual User Roles**: Separate interfaces and permissions for regular Users and Admins.
* **User Management**: Admins can add, delete, and manage user credentials.
* **Data Management**: Users and Admins can upload and manage PDF documents.
* **VectorDB Integration**: Uploaded documents can be ingested into a vector database for RAG.
* **Interactive Chat**: Users can chat with the RAG model, which utilizes the ingested documents.
* **Containerized**: Fully containerized with Docker for easy setup and deployment.

## Deployment to GCP with Cloud Run

This is the recommended method for deploying the application to production.

### Step 1: Build and Push Docker Images

1.  **Authenticate with GCP**: Make sure you have the `gcloud` CLI installed and authenticated.
    ```bash
    gcloud auth login
    gcloud auth configure-docker
    ```

2.  **Enable Services**: Enable Artifact Registry and Cloud Run API in your GCP project.

3.  **Build the Images**: From the root directory, build both images using Docker Compose.
    ```bash
    docker-compose build
    ```

4.  **Tag and Push Images**: Tag the built images and push them to Google Artifact Registry. Replace `[PROJECT-ID]` with your GCP Project ID.
    ```bash
    # Tag the backend image
    docker tag rag-backend gcr.io/[PROJECT-ID]/rag-backend:latest
    # Push the backend image
    docker push gcr.io/[PROJECT-ID]/rag-backend:latest

    # Tag the frontend image
    docker tag rag-frontend gcr.io/[PROJECT-ID]/rag-frontend:latest
    # Push the frontend image
    docker push gcr.io/[PROJECT-ID]/rag-frontend:latest
    ```

### Step 2: Deploy the Backend Service

1.  Deploy the backend image to Cloud Run.
    ```bash
    gcloud run deploy rag-backend \
      --image gcr.io/[PROJECT-ID]/rag-backend:latest \
      --platform managed \
      --region [YOUR_REGION] \
      --allow-unauthenticated \
      --set-env-vars="ADMIN_USERNAME=admin,ADMIN_PASSWORD=[CHOOSE_A_SECURE_PASSWORD]"
    ```
2.  After deployment, Cloud Run will provide a public URL for your backend service. **Copy this URL.**

### Step 3: Deploy the Frontend Service

1.  Deploy the frontend image to Cloud Run, making sure to provide the backend's public URL as an environment variable.
    ```bash
    gcloud run deploy rag-frontend \
      --image gcr.io/[PROJECT-ID]/rag-frontend:latest \
      --platform managed \
      --region [YOUR_REGION] \
      --allow-unauthenticated \
      --set-env-vars="BACKEND_URL=[PASTE_THE_BACKEND_URL_HERE]"
    ```
2.  Your application is now live! Access the frontend using the URL provided by Cloud Run.

## Local Development using Docker Compose

To run the entire stack locally for development and testing:

1.  **Build and Start Containers**: From the root directory, run:
    ```bash
    docker-compose up --build
    ```
2.  **Access Services**:
    * **Frontend**: `http://localhost:8501` (for Streamlit) or `http://localhost:7860` (for Gradio)
    * **Backend**: `http://localhost:8000`

## Load Testing

The `tests/` directory contains scripts for load testing the application using Locust. See the `tests/README.md` for detailed instructions on how to prepare the environment and run the tests.
