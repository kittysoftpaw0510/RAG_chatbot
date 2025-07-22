import requests
import os
from requests.auth import HTTPBasicAuth
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# --- Configuration ---
# This should match the admin credentials for your running backend application
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpassword" # Use the password from your docker-compose.yml
BASE_URL = "http://127.0.0.1:8000"
NUM_USERS_TO_CREATE = 20
NUM_PDFS_TO_CREATE = 10
PDF_DIR = "test_pdfs"

def create_test_users():
    """
    Checks for existing users and creates only the missing ones.
    This is an idempotent operation, safe to run multiple times.
    """
    print("--- Creating Test Users ---")
    auth = HTTPBasicAuth(ADMIN_USERNAME, ADMIN_PASSWORD)
    
    # --- NEW LOGIC: First, get a list of all existing users ---
    try:
        res = requests.get(f"{BASE_URL}/admin/users", auth=auth)
        if res.status_code != 200:
            print(f"ERROR: Could not fetch existing users. Status: {res.status_code} - {res.text}")
            print("Please ensure your admin credentials are correct and the backend is running.")
            return False
        
        # Create a set for efficient lookup
        existing_users = {user['username'] for user in res.json()}
        print(f"Found {len(existing_users)} existing users.")

    except requests.exceptions.ConnectionError:
        print(f"\nERROR: Could not connect to the backend at {BASE_URL}.")
        print("Please ensure your backend application is running before executing this script.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while fetching users: {e}")
        return False

    # --- NEW LOGIC: Loop and create only if the user does not exist ---
    for i in range(1, NUM_USERS_TO_CREATE + 1):
        username = f"testuser{i}"
        password = "password" # All test users will have the same simple password
        
        if username in existing_users:
            print(f"User already exists, skipping: {username}")
            continue # Move to the next user in the loop
        
        # If we reach here, the user does not exist, so we create them.
        print(f"User '{username}' not found, attempting to create...")
        try:
            res = requests.post(
                f"{BASE_URL}/admin/users",
                json={"username": username, "password": password},
                auth=auth
            )
            if res.status_code == 200:
                print(f"Successfully created user: {username}")
            else:
                # This would be an unexpected error now
                print(f"Failed to create user {username}: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"An unexpected error occurred during user creation: {e}")
            # Decide if you want to stop or continue on a single failure
            # return False 
            
    print("--- User creation process finished. ---")
    return True

def create_dummy_pdfs():
    """Creates a directory with simple, unique PDF files for testing uploads."""
    print("\n--- Creating Dummy PDF Files ---")
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)
        print(f"Created directory: {PDF_DIR}")

    for i in range(1, NUM_PDFS_TO_CREATE + 1):
        file_path = os.path.join(PDF_DIR, f"test_document_{i}.pdf")
        if os.path.exists(file_path):
            print(f"File already exists: {file_path}")
            continue
        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            c.drawString(100, 750, f"This is a test document.")
            c.drawString(100, 735, f"File number: {i}")
            c.drawString(100, 720, "This file is for load testing purposes.")
            c.save()
            print(f"Successfully created PDF: {file_path}")
        except Exception as e:
            print(f"Failed to create PDF {file_path}: {e}")
            return False
            
    print("--- PDF creation process finished. ---")
    return True

if __name__ == "__main__":
    print("Starting test environment setup...")
    if create_test_users():
        create_dummy_pdfs()
    print("\nSetup complete.")

