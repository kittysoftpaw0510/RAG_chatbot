import requests
import os
from requests.auth import HTTPBasicAuth

class PDFDataManager:
    def __init__(self, username="", password="", base_url="http://127.0.0.1:8000"):
        self.username = username
        self.password = password
        self.base_url = base_url
        self.auth = HTTPBasicAuth(username, password)

    def upload_folder(self):
        folder_path = input("Enter the folder path containing PDFs to upload: ").strip()
        if not os.path.isdir(folder_path):
            print("Invalid folder path.")
            return
        pdf_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(folder_path, f))
        ]
        if not pdf_files:
            print("No PDF files found in the folder.")
            return
        files = [
            ("files", (os.path.basename(path), open(path, "rb"), "application/pdf"))
            for path in pdf_files
        ]
        try:
            res = requests.post(f"{self.base_url}/pdf/upload", files=files, auth=self.auth)
            for _, file_tuple in files:
                file_tuple[1].close()
            if res.status_code == 200:
                print("Uploaded:", res.json().get("uploaded", []))
            else:
                print("Error:", res.json().get("error", "Failed to upload PDFs."))
        except Exception as e:
            print("Error uploading PDFs:", str(e))

    def upload_pdfs(self):
        pdf_paths = input("Enter PDF file paths to upload (comma separated): ").split(",")
        pdf_paths = [p.strip() for p in pdf_paths if p.strip()]
        files = [("files", (os.path.basename(path), open(path, "rb"), "application/pdf")) for path in pdf_paths if os.path.isfile(path)]
        if not files:
            print("No valid PDF files provided.")
            return
        res = requests.post(f"{self.base_url}/pdf/upload", files=files, auth=self.auth)
        for _, file_tuple in files:
            file_tuple[1].close()
        if res.status_code == 200:
            print("Uploaded:", res.json().get("uploaded", []))
        else:
            print("Error:", res.json().get("error", "Failed to upload PDFs."))

    def remove_all_pdfs(self):
        res = requests.delete(f"{self.base_url}/pdf", auth=self.auth)
        if res.status_code == 200:
            print("Deleted:", res.json().get("deleted", []))
        else:
            print("Error:", res.json().get("error", "Failed to delete all PDFs."))

    def remove_pdf_by_filename(self):
        res = requests.get(f"{self.base_url}/pdf", auth=self.auth)
        if res.status_code == 200:
            pdfs = res.json().get("pdfs", [])
            if pdfs:
                print("Available PDFs:")
                for i, pdf in enumerate(pdfs, 1):
                    print(f"{i}. {pdf}")
            else:
                print("No PDFs found.")
        else:
            print("Error fetching available PDFs.")
        filename = input("Enter PDF filename to delete: ").strip()
        if not filename:
            print("Filename cannot be empty.")
            return
        res = requests.delete(f"{self.base_url}/pdf/{filename}", auth=self.auth)
        if res.status_code == 200:
            print("Deleted:", res.json().get("deleted", filename))
        else:
            print("Error:", res.json().get("error", f"Failed to delete {filename}."))

    def ingest_all_pdfs(self):
        res = requests.post(f"{self.base_url}/pdf/ingest", auth=self.auth)
        if res.status_code == 200:
            print("Ingested:", res.json())
        else:
            print("Error:", res.json().get("error", "Failed to ingest all PDFs."))

    def ingest_pdf_by_filename(self):
        res = requests.get(f"{self.base_url}/pdf", auth=self.auth)
        if res.status_code == 200:
            pdfs = res.json().get("pdfs", [])
            if pdfs:
                print("Available PDFs:")
                for i, pdf in enumerate(pdfs, 1):
                    print(f"{i}. {pdf}")
            else:
                print("No PDFs found.")
        else:
            print("Error fetching available PDFs.")
        filename = input("Enter PDF filename to ingest: ").strip()
        if not filename:
            print("Filename cannot be empty.")
            return
        res = requests.post(f"{self.base_url}/pdf/ingest/{filename}", auth=self.auth)
        if res.status_code == 200:
            print("Ingested:", res.json())
        else:
            print("Error:", res.json().get("error", f"Failed to ingest {filename}."))

    def list_available_pdfs(self):
        res = requests.get(f"{self.base_url}/pdf", auth=self.auth)
        if res.status_code == 200:
            pdfs = res.json().get("pdfs", [])
            if pdfs:
                print("Available PDFs in data folder:")
                for i, pdf in enumerate(pdfs, 1):
                    print(f"{i}. {pdf}")
            else:
                print("No PDFs found in data folder.")
        else:
            print("Error fetching PDFs.")

def show_menu(manager):
    print("\n=== PDF Data Management ===")
    print("    1. Upload all PDFs in a folder")
    print("    2. Upload PDF(s)")
    print("    3. Remove all PDFs")
    print("    4. Remove PDF by filename")
    print("    5. Ingest all PDFs")
    print("    6. Ingest PDF by filename")
    print("    7. List available PDFs in data folder")
    print("    8. Exit")
    choice = input("\nEnter your choice (1-8): ").strip()
    if choice == "1":
        manager.upload_folder()
    elif choice == "2":
        manager.upload_pdfs()
    elif choice == "3":
        manager.remove_all_pdfs()
    elif choice == "4":
        manager.remove_pdf_by_filename()
    elif choice == "5":
        manager.ingest_all_pdfs()
    elif choice == "6":
        manager.ingest_pdf_by_filename()
    elif choice == "7":
        manager.list_available_pdfs()
    elif choice == "8":
        print("Exiting...")
        return False
    else:
        print("Invalid choice. Please try again.")
    return True

if __name__ == "__main__":
    # base_url = "http://127.0.0.1:8000"
    base_url = "http://40.82.161.202:8000"

    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    manager = PDFDataManager(username, password, base_url)
    while True:
        if not show_menu(manager):
            break
