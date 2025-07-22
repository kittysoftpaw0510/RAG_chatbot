import random
import os
import logging
from locust import HttpUser, task, between, events
from requests.auth import HTTPBasicAuth

# --- Event Hooks for Detailed Logging ---
# This code will run for every request that Locust makes.

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response,
               context, exception, start_time, url, **kwargs):
    """
    Event listener that logs details for every single request made.
    """
    if exception:
        # Log failed requests
        logging.error(
            f"Request to '{name}' failed with exception {exception}"
        )
    else:
        # Log successful requests
        logging.info(
            f"Request to '{name}' success | Status: {response.status_code} | Time: {round(response_time)}ms"
        )

# --- Configuration ---
NUM_TEST_USERS = 20
PDF_DIR = "test_pdfs"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpassword" # Should match your docker-compose.yml or backend config

# --- Helper Functions ---
def get_random_user_credentials():
    """Picks a random user from the pool of test users."""
    user_id = random.randint(1, NUM_TEST_USERS)
    return f"testuser{user_id}", "password"

def get_random_pdf():
    """Picks a random PDF file from the test directory."""
    try:
        pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
        if not pdf_files:
            return None, None
        
        random_pdf_name = random.choice(pdf_files)
        pdf_path = os.path.join(PDF_DIR, random_pdf_name)
        
        # We need to return the file name and a file-like object
        return random_pdf_name, open(pdf_path, 'rb')
    except FileNotFoundError:
        print(f"ERROR: The '{PDF_DIR}' directory was not found. Please run the setup script first.")
        return None, None
    except Exception as e:
        print(f"An error occurred while getting a random PDF: {e}")
        return None, None

class WebsiteUser(HttpUser):
    """
    Defines the behavior of a regular user. This will be the majority of the load.
    Each user will wait between 30 and 40 seconds between completing tasks.
    """
    wait_time = between(30, 40)
    # This weight means for every 1 AdminUser, 10 WebsiteUsers will be spawned.
    weight = 10
    
    def on_start(self):
        """
        This method is called when a new WebsiteUser is started.
        It sets the user's credentials and performs an initial authentication check to simulate a login.
        """
        username, password = get_random_user_credentials()
        self.auth = HTTPBasicAuth(username, password)
        self.username = username
        
        # Perform an initial auth check to simulate a login request
        self.client.get(
            "/user/auth/check",
            auth=self.auth,
            name="/user/auth/check"
        )

    @task(3) # This task is 3 times more likely to be chosen than upload_pdf
    def chat(self):
        """Simulates a user sending a chat message."""
        chat_messages = [
            "Hello, can you help me?",
            "What is the capital of France?",
            "Tell me about the documents I have uploaded.",
            "Summarize the key points.",
        ]
        message = random.choice(chat_messages)
        
        self.client.post(
            "/user/chat",
            json={"user_id": self.username, "message": message},
            auth=self.auth,
            name="/user/chat" # Group all chat requests under one name in stats
        )

    @task(1) # This task is less frequent than chatting
    def upload_pdf(self):
        """Simulates a user uploading a random PDF."""
        pdf_name, pdf_file_object = get_random_pdf()
        
        if not pdf_name or not pdf_file_object:
            return # Skip this task if we couldn't get a PDF

        files_to_send = [("files", (pdf_name, pdf_file_object, "application/pdf"))]
        data = {"is_public": 0} # Assume private upload for testing
        
        try:
            self.client.post(
                "/user/pdf/upload",
                files=files_to_send,
                data=data,
                auth=self.auth,
                name="/user/pdf/upload"
            )
        finally:
            # It's very important to close the file object after the request
            if pdf_file_object:
                pdf_file_object.close()

class AdminUser(HttpUser):
    """
    Defines the behavior of an admin user. This will be a minority of the load.
    The wait time is slightly longer to simulate less frequent admin activity.
    """
    wait_time = between(50, 60)
    # This weight means for every 10 WebsiteUsers, 1 AdminUser will be spawned.
    weight = 1

    def on_start(self):
        """
        Called when a new AdminUser is started.
        Sets the admin's credentials and performs an initial authentication check to simulate a login.
        """
        self.auth = HTTPBasicAuth(ADMIN_USERNAME, ADMIN_PASSWORD)
        
        # Perform an initial auth check to simulate a login request
        self.client.get(
            "/admin/auth/check",
            auth=self.auth,
            name="/admin/auth/check"
        )
    
    @task(5)
    def list_all_users(self):
        """Simulates an admin viewing the list of all users."""
        self.client.get(
            "/admin/users",
            auth=self.auth,
            name="/admin/users"
        )

    @task(5)
    def list_all_pdfs(self):
        """Simulates an admin viewing the list of all PDFs."""
        self.client.get(
            "/admin/pdf",
            auth=self.auth,
            name="/admin/pdf"
        )

    @task(2)
    def view_user_chat_history(self):
        """Simulates an admin viewing a random user's chat history."""
        random_user_id = f"testuser{random.randint(1, NUM_TEST_USERS)}"
        
        self.client.get(
            f"/admin/chat/history/{random_user_id}",
            auth=self.auth,
            name="/admin/chat/history/[user_id]" # Group all history requests together
        )
