import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from utils.sqlitedb import get_all_pdfs, get_pdfs_by_user, ingest
from utils.vectordb import insert_new_chunks

load_dotenv(".env")

PERSIST_DIR = os.getenv("PERSIST_DIR", "")
DATA_DIR = os.path.join(PERSIST_DIR, "data")

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

####################################
# Admin
####################################

def ingest_all_pdfs():
    """Admin: Ingest all PDFs in public folder."""
    public_dir = os.path.join(DATA_DIR, "public")
    if not os.path.exists(public_dir):
        print(f"No public directory: {public_dir}")
        return
    pdfs = [f for f in os.listdir(public_dir) if f.lower().endswith('.pdf')]
    if not pdfs:
        print("No public PDFs found.")
        return
    for pdf in pdfs:
        file_path = os.path.join(public_dir, pdf)
        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            chunks = splitter.split_documents(docs)
            for c in chunks:
                c.metadata = {"user_id": "public", "filename": pdf, "source": pdf, "is_public": 1}
            insert_new_chunks(chunks)
            ingest(pdf, "public", 1)
            print(f"Ingested public PDF: {pdf}")
        except Exception as e:
            print(f"Failed to ingest {pdf}: {e}")

def ingest_one_pdf_admin(filename: str, user_id: str = None):
    """Admin: Ingest one PDF for any user or for all (public). If user_id is None, treat as public."""
    all_pdfs = get_all_pdfs()
    pdf_info = None
    for pdf in all_pdfs:
        if pdf["filename"] == filename:
            pdf_info = pdf
            break
    if not pdf_info:
        print(f"PDF '{filename}' not found in database.")
        return
    # Correct file path logic
    if pdf_info["is_public"] == 1:
        file_path = os.path.join(DATA_DIR, "public", filename)
    else:
        file_path = os.path.join(DATA_DIR, pdf_info["uploaded_by"], filename)
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        chunks = splitter.split_documents(docs)
        if user_id:
            meta_user = user_id
            is_public = 0
        else:
            meta_user = "public"
            is_public = 1
        for c in chunks:
            c.metadata = {
                "user_id": meta_user,
                "filename": pdf_info["filename"],
                "source": pdf_info["filename"],
                "is_public": is_public
            }
        insert_new_chunks(chunks)
        ingest(pdf_info["filename"], meta_user, is_public)
        print(f"Admin ingested PDF: {filename} for user: {meta_user}")
    except Exception as e:
        print(f"Failed to ingest {filename}: {e}")

def ingest_one_pdf_public(filename: str):
    """Admin: Ingest one PDF as public (user_id='public', is_public=1)."""
    all_pdfs = get_all_pdfs()
    pdf_info = None
    for pdf in all_pdfs:
        if pdf["filename"] == filename:
            pdf_info = pdf
            break
    if not pdf_info:
        print(f"PDF '{filename}' not found in database.")
        return
    # if pdf_info["is_public"] != 1:
    #     print(f"ERROR: Only public PDFs can be ingested as public.")
    #     return
    file_path = os.path.join(DATA_DIR, "public", filename)
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        chunks = splitter.split_documents(docs)
        for c in chunks:
            c.metadata = {
                "user_id": "public",
                "filename": pdf_info["filename"],
                "source": pdf_info["filename"],
                "is_public": 1
            }
        insert_new_chunks(chunks)
        ingest(pdf_info["filename"], "public", 1)
        print(f"Admin ingested PDF: {filename} as public.")
    except Exception as e:
        print(f"Failed to ingest {filename}: {e}")

def ingest_one_pdf_private(filename: str, user_id: str):
    """Admin: Ingest one PDF for a specific user (user_id, is_public=0)."""
    all_pdfs = get_all_pdfs()
    pdf_info = None
    print("TEST", all_pdfs)
    for pdf in all_pdfs:
        if pdf["filename"] == filename:
            pdf_info = pdf
            break
    if not pdf_info:
        print(f"PDF '{filename}' not found in database.")
        return
    # Determine correct file path
    if pdf_info["is_public"] == 1:
        file_path = os.path.join(DATA_DIR, "public", filename)
    else:
        file_path = os.path.join(DATA_DIR, pdf_info["uploaded_by"], filename)
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        chunks = splitter.split_documents(docs)
        for c in chunks:
            c.metadata = {
                "user_id": user_id,
                "filename": pdf_info["filename"],
                "source": pdf_info["filename"],
                "is_public": 0
            }
        insert_new_chunks(chunks)
        ingest(pdf_info["filename"], user_id, 0)
        print(f"Admin ingested PDF: {filename} for user: {user_id}.")
    except Exception as e:
        print(f"Failed to ingest {filename}: {e}")

# Deprecated: use the new explicit functions above

####################################
# User
####################################

def ingest_my_all_pdfs(user_id: str = None, is_public: bool = False):
    """User: Ingest all PDFs uploaded by this user. Only for me."""
    if not user_id:
        print("user_id required")
        return
    pdfs = get_pdfs_by_user(user_id)
    if not pdfs:
        print(f"No PDFs found for user {user_id}")
        return
    for pdf in pdfs:
        if is_public and not pdf["is_public"]:
            continue
        file_path = os.path.join(DATA_DIR, pdf["filepath"])
        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            chunks = splitter.split_documents(docs)
            for c in chunks:
                c.metadata = {"user_id": user_id, "filename": pdf["filename"], "source": pdf["filename"], "is_public": pdf["is_public"]}
            insert_new_chunks(chunks)
            ingest(pdf["filename"], user_id, pdf["is_public"])
            print(f"User {user_id} ingested PDF: {pdf['filename']}")
        except Exception as e:
            print(f"Failed to ingest {pdf['filename']}: {e}")

def ingest_one_pdf_user(filename: str, user_id: str = None):
    """User: Ingest one PDF, but can only ingest PDFs which user uploaded."""
    if not user_id:
        print("user_id required")
        return
    user_pdfs = get_pdfs_by_user(user_id)
    pdf_info = None
    for pdf in user_pdfs:
        if pdf["filename"] == filename:
            pdf_info = pdf
            break
    if not pdf_info:
        print(f"PDF '{filename}' not found or not permitted for user {user_id}.")
        return
    file_path = os.path.join(DATA_DIR, pdf_info["filepath"])
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        chunks = splitter.split_documents(docs)
        for c in chunks:
            c.metadata = {"user_id": user_id, "filename": pdf_info["filename"], "source": pdf_info["filename"], "is_public": pdf_info["is_public"]}
        insert_new_chunks(chunks)
        ingest(pdf_info["filename"], user_id, pdf_info["is_public"])
        print(f"User {user_id} ingested PDF: {filename}")
    except Exception as e:
        print(f"Failed to ingest {filename}: {e}")

if __name__ == "__main__":
    print("Ingest all public PDFs (admin)")
    ingest_all_pdfs()