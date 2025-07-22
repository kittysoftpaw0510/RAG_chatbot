import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, Body, Form
from fastapi.security import HTTPBasicCredentials
from typing import List
from routes.user.user_auth import verify_user_credentials
import utils.sqlitedb as db
from utils.logger import log_event

PERSIST_DIR = os.getenv("PERSIST_DIR", "")
DATA_DIR = os.path.join(PERSIST_DIR, "data")

router = APIRouter()

@router.post("/user/pdf/upload")
def upload_pdf(
    files: List[UploadFile] = File(...),
    credentials: HTTPBasicCredentials = Depends(verify_user_credentials),
    is_public: int = Form(0)
):
    uploaded = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue
        if is_public:
            save_dir = os.path.join(DATA_DIR, "public")
            db_path = os.path.join("public", file.filename)
        else:
            save_dir = os.path.join(DATA_DIR, credentials.username)
            db_path = os.path.join(credentials.username, file.filename)
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        db.add_pdf(file.filename, credentials.username, is_public, db_path)
        uploaded.append(file.filename)
        log_event(credentials.username, "upload_pdf", f"filename={file.filename}, is_public={is_public}")
    if not uploaded:
        raise HTTPException(status_code=400, detail="No valid PDFs uploaded.")
    return {"uploaded": uploaded}

@router.get("/user/pdf")
def list_pdfs(credentials: HTTPBasicCredentials = Depends(verify_user_credentials)):
    pdfs = db.get_pdfs_by_user(credentials.username)
    log_event(credentials.username, "list_pdfs", f"count={len(pdfs)}")
    return {"pdfs": pdfs}

@router.post("/user/pdf/delete")
def delete_pdf(
    data: dict = Body(...),
    credentials: HTTPBasicCredentials = Depends(verify_user_credentials)
):
    filenames = data.get("filenames")
    if not filenames or not isinstance(filenames, list):
        raise HTTPException(status_code=400, detail="Missing or invalid 'filenames' (must be a list).")
    deleted = []
    errors = []
    for filename in filenames:
        pdfs = db.get_pdfs_by_user(credentials.username)
        pdf_info = next((pdf for pdf in pdfs if pdf["filename"] == filename), None)
        if not pdf_info:
            errors.append({"filename": filename, "error": "Not found in database"})
            continue
        if pdf_info["is_public"] == 1:
            abs_file_path = os.path.join(DATA_DIR, "public", filename)
        else:
            abs_file_path = os.path.join(DATA_DIR, credentials.username, filename)
        if not os.path.exists(abs_file_path):
            errors.append({"filename": filename, "error": "File not found on disk"})
            continue
        try:
            os.remove(abs_file_path)
        except Exception as e:
            errors.append({"filename": filename, "error": str(e)})
            continue
        success = db.delete_pdf_by_filename(filename)
        if not success:
            errors.append({"filename": filename, "error": "Failed to delete from database"})
            continue
        deleted.append(filename)
        log_event(credentials.username, "delete_pdf", f"filename={filename}")
    return {"deleted": deleted, "errors": errors}

@router.get("/user/ingested_pdfs")
def list_ingested_pdfs(credentials: HTTPBasicCredentials = Depends(verify_user_credentials)):
    from utils.sqlitedb import get_ingested_pdfs_by_user
    pdfs = get_ingested_pdfs_by_user(credentials.username)
    log_event(credentials.username, "list_ingested_pdfs", f"count={len(pdfs)}")
    return {"ingested_pdfs": pdfs}
