import requests
from requests.auth import HTTPBasicAuth
import getpass
import os
from client_logger import log_client_event
import pprint

BASE_URL = "http://127.0.0.1:8000"

class UserToolsManager:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.auth = HTTPBasicAuth(username, password)

    def upload_pdfs(self):
        filepaths = input("Enter PDF file paths (comma separated): ").split(",")
        files = [("files", (fp.strip(), open(fp.strip(), "rb"), "application/pdf")) for fp in filepaths if fp.strip()]
        is_public = input("Is public? (1 for yes, 0 for no): ").strip()
        res = requests.post(f"{BASE_URL}/user/pdf/upload", files=files, data={"is_public": is_public}, auth=self.auth)
        log_client_event(self.username, "user_upload_pdfs", "success" if res.status_code == 200 else "fail", f"files={filepaths}, is_public={is_public}, response={res.text}", is_admin=False)
        pprint.pprint(res.json())

    def upload_all_pdfs_from_folder(self):
        folder = input("Enter folder path: ").strip()
        files = []
        for fname in os.listdir(folder):
            if fname.lower().endswith(".pdf"):
                files.append(("files", (fname, open(os.path.join(folder, fname), "rb"), "application/pdf")))
        is_public = input("Is public? (1 for yes, 0 for no): ").strip()
        res = requests.post(f"{BASE_URL}/user/pdf/upload", files=files, data={"is_public": is_public}, auth=self.auth)
        log_client_event(self.username, "user_upload_folder", "success" if res.status_code == 200 else "fail", f"folder={folder}, is_public={is_public}, response={res.text}", is_admin=False)
        pprint.pprint(res.json())

    def list_my_pdfs(self):
        res = requests.get(f"{BASE_URL}/user/pdf", auth=self.auth)
        log_client_event(self.username, "user_list_pdfs", "success" if res.status_code == 200 else "fail", f"response={res.text}", is_admin=False)
        pprint.pprint(res.json())

    def ingest_my_pdf(self):
        filename = input("Enter filename to ingest: ").strip()
        res = requests.post(f"{BASE_URL}/user/vectordb/ingest/one/{filename}", auth=self.auth)
        log_client_event(self.username, "user_ingest_pdf", "success" if res.status_code == 200 else "fail", f"filename={filename}, response={res.text}", is_admin=False)
        pprint.pprint(res.json())

    def ingest_all_my_pdfs(self):
        res = requests.post(f"{BASE_URL}/user/vectordb/ingest/all", auth=self.auth)
        log_client_event(self.username, "user_ingest_all_pdfs", "success" if res.status_code == 200 else "fail", f"response={res.text}", is_admin=False)
        pprint.pprint(res.json())

    def change_password(self):
        print("Not implemented. Please contact admin.")

    def delete_my_pdf_from_chroma_by_filename(self):
        filename = input("Enter filename to remove from vectordb: ").strip()
        res = requests.delete(f"{BASE_URL}/user/vectordb/pdf/one/{filename}", auth=self.auth)
        log_client_event(self.username, "user_remove_pdf_vectordb", "success" if res.status_code == 200 else "fail", f"filename={filename}, response={res.text}", is_admin=False)
        pprint.pprint(res.json())

    def delete_all_my_pdfs_from_chroma(self):
        res = requests.delete(f"{BASE_URL}/user/vectordb/pdf/all", auth=self.auth)
        log_client_event(self.username, "user_remove_all_pdfs_vectordb", "success" if res.status_code == 200 else "fail", f"response={res.text}", is_admin=False)
        pprint.pprint(res.json())

    def delete_my_pdf_from_data_by_filename(self):
        filename = input("Enter filename to delete from storage: ").strip()
        res = requests.post(f"{BASE_URL}/user/pdf/delete", json={"filenames": [filename]}, auth=self.auth)
        log_client_event(self.username, "user_delete_pdf_data", "success" if res.status_code == 200 else "fail", f"filename={filename}, response={res.text}", is_admin=False)
        pprint.pprint(res.json())

    def delete_all_my_pdfs_from_data(self):
        res = requests.get(f"{BASE_URL}/user/pdf", auth=self.auth)
        pdfs = res.json().get("pdfs", [])
        filenames = [pdf["filename"] for pdf in pdfs]
        if not filenames:
            print("No PDFs to delete.")
            return
        res = requests.post(f"{BASE_URL}/user/pdf/delete", json={"filenames": filenames}, auth=self.auth)
        log_client_event(self.username, "user_delete_all_pdfs_data", "success" if res.status_code == 200 else "fail", f"filenames={filenames}, response={res.text}", is_admin=False)
        pprint.pprint(res.json())

    def list_ingested_pdfs(self):
        res = requests.get(f"{BASE_URL}/user/ingested_pdfs", auth=self.auth)
        log_client_event(self.username, "user_list_ingested_pdfs", "success" if res.status_code == 200 else "fail", f"response={res.text}", is_admin=False)
        pprint.pprint(res.json())

    def main_menu(self):
        while True:
            print("\n=== User Main Menu ===")
            print("1. Upload PDFs")
            print("2. Upload all PDFs from folder")
            print("3. List my PDFs")
            print("4. Ingest a PDF")
            print("5. Ingest all my PDFs")
            print("6. List my ingested PDFs")
            print("7. Delete a PDF from storage")
            print("8. Delete all my PDFs from storage")
            print("9. Remove a PDF from vectordb")
            print("10. Remove all my PDFs from vectordb")
            print("0. Exit")
            choice = input("Select option: ").strip()
            if choice == "1":
                self.upload_pdfs()
            elif choice == "2":
                self.upload_all_pdfs_from_folder()
            elif choice == "3":
                self.list_my_pdfs()
            elif choice == "4":
                self.ingest_my_pdf()
            elif choice == "5":
                self.ingest_all_my_pdfs()
            elif choice == "6":
                self.list_ingested_pdfs()
            elif choice == "7":
                self.delete_my_pdf_from_data_by_filename()
            elif choice == "8":
                self.delete_all_my_pdfs_from_data()
            elif choice == "9":
                self.delete_my_pdf_from_chroma_by_filename()
            elif choice == "10":
                self.delete_all_my_pdfs_from_chroma()
            elif choice == "0":
                log_client_event(self.username, "user_exit", "success", "user exited", is_admin=False)
                print("Goodbye!")
                break
            else:
                print("Invalid option.")

def authenticate():
    print("=== User Login ===")
    while True:
        username = input("User ID: ").strip()
        password = getpass.getpass("Password: ")
        try:
            res = requests.get(f"{BASE_URL}/user/auth/check", auth=HTTPBasicAuth(username, password))
            if res.status_code == 200:
                print("✅ Authentication successful!\n")
                log_client_event(username, "user_login", "success", "login succeeded", is_admin=False)
                return username, password
            else:
                print("❌ Incorrect username or password. Please try again.\n")
                log_client_event(username, "user_login", "fail", f"login failed: {res.text}", is_admin=False)
        except Exception as e:
            print(f"❌ Error connecting to server: {e}\n")
            log_client_event(username, "user_login", "fail", f"connection error: {e}", is_admin=False)

if __name__ == "__main__":
    username, password = authenticate()
    manager = UserToolsManager(username, password)
    manager.main_menu()
