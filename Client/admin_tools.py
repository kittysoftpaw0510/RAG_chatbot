import getpass
import requests
from requests.auth import HTTPBasicAuth
from client_logger import log_client_event
import pprint

BASE_URL = "http://127.0.0.1:8000"

def admin_login():
    print("=== Admin Login ===")
    while True:
        username = input("Admin username: ").strip()
        password = getpass.getpass("Password: ")
        try:
            res = requests.get(f"{BASE_URL}/admin/auth/check", auth=HTTPBasicAuth(username, password))
            if res.status_code == 200:
                print("✅ Admin authentication successful!\n")
                log_client_event(username, "admin_login", "success", "login succeeded", is_admin=True)
                return username, password
            else:
                print("❌ Incorrect admin credentials. Please try again.\n")
                log_client_event(username, "admin_login", "fail", f"login failed: {res.text}", is_admin=True)
        except Exception as e:
            print(f"❌ Error connecting to server: {e}\n")
            log_client_event(username, "admin_login", "fail", f"connection error: {e}", is_admin=True)

def user_management_menu(auth):
    while True:
        print("\n--- User Management ---")
        print("1. List users")
        print("2. Add user")
        print("3. Delete user")
        print("4. Reset user password")
        print("0. Back to main menu")
        choice = input("Select option: ").strip()
        if choice == "1":
            res = requests.get(f"{BASE_URL}/admin/users", auth=auth)
            log_client_event(auth.username, "admin_list_users", "success" if res.status_code == 200 else "fail", f"response={res.text}", is_admin=True)
            print("\nUsers:")
            pprint.pprint(res.json())
        elif choice == "2":
            username = input("New username: ").strip()
            password = getpass.getpass("New password: ")
            res = requests.post(f"{BASE_URL}/admin/users", json={"username": username, "password": password}, auth=auth)
            log_client_event(auth.username, "admin_add_user", "success" if res.status_code == 200 else "fail", f"username={username}, response={res.text}", is_admin=True)
            pprint.pprint(res.json())
        elif choice == "3":
            username = input("Username to delete: ").strip()
            res = requests.delete(f"{BASE_URL}/admin/users/{username}", auth=auth)
            log_client_event(auth.username, "admin_delete_user", "success" if res.status_code == 200 else "fail", f"username={username}, response={res.text}", is_admin=True)
            pprint.pprint(res.json())
        elif choice == "4":
            username = input("Username to reset password: ").strip()
            password = getpass.getpass("New password: ")
            res = requests.post(f"{BASE_URL}/admin/users/{username}/reset_password", json={"password": password}, auth=auth)
            log_client_event(auth.username, "admin_reset_password", "success" if res.status_code == 200 else "fail", f"username={username}, response={res.text}", is_admin=True)
            pprint.pprint(res.json())
        elif choice == "0":
            break
        else:
            print("Invalid option.")

def chat_management_menu(auth):
    while True:
        print("\n--- Chat Management ---")
        print("1. View user chat history")
        print("0. Back to main menu")
        choice = input("Select option: ").strip()
        if choice == "1":
            user_id = input("User ID: ").strip()
            res = requests.get(f"{BASE_URL}/admin/chat/history/{user_id}", auth=auth)
            log_client_event(auth.username, "admin_view_chat_history", "success" if res.status_code == 200 else "fail", f"user_id={user_id}, response={res.text}", is_admin=True)
            data = res.json()
            print(f"\nChat history for {user_id}:")
            pprint.pprint(data.get("history", []))
        elif choice == "0":
            break
        else:
            print("Invalid option.")

def data_management_menu(auth):
    while True:
        print("\n--- Data Management ---")
        print("1. Upload PDF(s)")
        print("2. Upload all PDFs from folder")
        print("3. List all PDFs")
        print("4. Delete PDF(s)")
        print("5. Delete all public PDFs")
        print("0. Back to main menu")
        choice = input("Select option: ").strip()
        if choice == "1":
            filepaths = input("Enter PDF file paths (comma separated): ").split(",")
            files = [("files", (fp.strip(), open(fp.strip(), "rb"), "application/pdf")) for fp in filepaths if fp.strip()]
            is_public = input("Is public? (1 for yes, 0 for no): ").strip()
            res = requests.post(f"{BASE_URL}/admin/pdf/upload", files=files, data={"is_public": is_public}, auth=auth)
            log_client_event(auth.username, "admin_upload_pdf", "success" if res.status_code == 200 else "fail", f"files={filepaths}, is_public={is_public}, response={res.text}", is_admin=True)
            pprint.pprint(res.json())
        elif choice == "2":
            folder = input("Enter folder path: ").strip()
            files = []
            import os
            for fname in os.listdir(folder):
                if fname.lower().endswith(".pdf"):
                    files.append(("files", (fname, open(os.path.join(folder, fname), "rb"), "application/pdf")))
            is_public = input("Is public? (1 for yes, 0 for no): ").strip()
            res = requests.post(f"{BASE_URL}/admin/pdf/upload", files=files, data={"is_public": is_public}, auth=auth)
            log_client_event(auth.username, "admin_upload_folder", "success" if res.status_code == 200 else "fail", f"folder={folder}, is_public={is_public}, response={res.text}", is_admin=True)
            pprint.pprint(res.json())
        elif choice == "3":
            res = requests.get(f"{BASE_URL}/admin/pdf", auth=auth)
            log_client_event(auth.username, "admin_list_pdfs", "success" if res.status_code == 200 else "fail", f"response={res.text}", is_admin=True)
            print("\nPDFs:")
            pprint.pprint(res.json())
        elif choice == "4":
            filenames = input("Enter filenames to delete (comma separated): ").split(",")
            res = requests.post(f"{BASE_URL}/admin/pdf/delete", json={"filenames": [f.strip() for f in filenames]}, auth=auth)
            log_client_event(auth.username, "admin_delete_pdf", "success" if res.status_code == 200 else "fail", f"filenames={filenames}, response={res.text}", is_admin=True)
            pprint.pprint(res.json())
        elif choice == "5":
            res = requests.post(f"{BASE_URL}/admin/pdf/delete_public", auth=auth)
            log_client_event(auth.username, "admin_delete_all_public_pdfs", "success" if res.status_code == 200 else "fail", f"response={res.text}", is_admin=True)
            pprint.pprint(res.json())
        elif choice == "0":
            break
        else:
            print("Invalid option.")

def vectordb_management_menu(auth):
    while True:
        print("\n--- VectorDB Management ---")
        print("1. Ingest all public PDFs")
        print("2. Ingest PDF by filename (public or specific user)")
        print("3. Remove PDF data by filename")
        print("4. Remove PDF data by user")
        print("5. List available PDF data")
        print("6. Clear all users' memory")
        print("7. Clear user memory by user ID")
        print("0. Back to main menu")
        choice = input("Select option: ").strip()
        if choice == "1":
            res = requests.post(f"{BASE_URL}/admin/vectordb/ingest/all", auth=auth)
            log_client_event(auth.username, "admin_vectordb_ingest_all", "success" if res.status_code == 200 else "fail", f"response={res.text}", is_admin=True)
            pprint.pprint(res.json())
        elif choice == "2":
            filename = input("Filename: ").strip()
            print("Ingest as:")
            print("1. Public")
            print("2. Specific user")
            ingest_choice = input("Select option: ").strip()
            if ingest_choice == "1":
                res = requests.post(f"{BASE_URL}/admin/vectordb/ingest/public/{filename}", auth=auth)
                log_client_event(auth.username, "admin_vectordb_ingest_public", "success" if res.status_code == 200 else "fail", f"filename={filename}, response={res.text}", is_admin=True)
                pprint.pprint(res.json())
            elif ingest_choice == "2":
                user_id = input("User ID: ").strip()
                res = requests.post(f"{BASE_URL}/admin/vectordb/ingest/private/{filename}?user_id={user_id}", auth=auth)
                log_client_event(auth.username, "admin_vectordb_ingest_private", "success" if res.status_code == 200 else "fail", f"filename={filename}, user_id={user_id}, response={res.text}", is_admin=True)
                pprint.pprint(res.json())
            else:
                print("Invalid option.")
        elif choice == "3":
            filename = input("Filename: ").strip()
            res = requests.delete(f"{BASE_URL}/admin/vectordb/pdf/{filename}", auth=auth)
            log_client_event(auth.username, "admin_vectordb_remove_pdf", "success" if res.status_code == 200 else "fail", f"filename={filename}, response={res.text}", is_admin=True)
            pprint.pprint(res.json())
        elif choice == "4":
            owner = input("User ID: ").strip()
            res = requests.delete(f"{BASE_URL}/admin/vectordb/pdf/user/{owner}", auth=auth)
            log_client_event(auth.username, "admin_vectordb_remove_by_user", "success" if res.status_code == 200 else "fail", f"owner={owner}, response={res.text}", is_admin=True)
            pprint.pprint(res.json())
        elif choice == "5":
            res = requests.get(f"{BASE_URL}/admin/vectordb/pdf", auth=auth)
            log_client_event(auth.username, "admin_vectordb_list", "success" if res.status_code == 200 else "fail", f"response={res.text}", is_admin=True)
            print("\nVectorDB Sources:")
            pprint.pprint(res.json())
        elif choice == "6":
            res = requests.delete(f"{BASE_URL}/admin/vectordb/memory", auth=auth)
            log_client_event(auth.username, "admin_vectordb_clear_all_memory", "success" if res.status_code == 200 else "fail", f"response={res.text}", is_admin=True)
            pprint.pprint(res.json())
        elif choice == "7":
            user_id = input("User ID: ").strip()
            res = requests.delete(f"{BASE_URL}/admin/vectordb/memory/{user_id}", auth=auth)
            log_client_event(auth.username, "admin_vectordb_clear_user_memory", "success" if res.status_code == 200 else "fail", f"user_id={user_id}, response={res.text}", is_admin=True)
            pprint.pprint(res.json())
        elif choice == "0":
            break
        else:
            print("Invalid option.")

def main():
    username, password = admin_login()
    auth = HTTPBasicAuth(username, password)
    while True:
        print("\n=== Admin Main Menu ===")
        print("1. User Management")
        print("2. Chat Management")
        print("3. Data Management")
        print("4. VectorDB Management")
        print("0. Exit")
        choice = input("Select option: ").strip()
        if choice == "1":
            user_management_menu(auth)
        elif choice == "2":
            chat_management_menu(auth)
        elif choice == "3":
            data_management_menu(auth)
        elif choice == "4":
            vectordb_management_menu(auth)
        elif choice == "0":
            log_client_event(auth.username, "admin_exit", "success", "admin exited", is_admin=True)
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main() 
