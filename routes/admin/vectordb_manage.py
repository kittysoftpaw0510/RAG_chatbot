import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from typing import Optional
from routes.admin.admin_auth import verify_admin_credentials
import utils.ingest as ingest
import utils.vectordb as vectordb
from utils.logger import log_event

router = APIRouter()

@router.post("/admin/vectordb/ingest/all")
def ingest_all(credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)):
    try:
        ingest.ingest_all_pdfs()
        log_event(credentials.username, "admin_ingest_all_pdfs", "all public PDFs ingested")
        return {"detail": "All public PDFs ingested."}
    except Exception as e:
        log_event(credentials.username, "admin_ingest_all_pdfs_failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/vectordb/ingest/one/{filename}")
def ingest_by_filename(filename: str, credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)):
    try:
        ingest.ingest_one_pdf_admin(filename)
        log_event(credentials.username, "admin_ingest_pdf", f"filename={filename}")
        return {"detail": f"PDF '{filename}' ingested."}
    except Exception as e:
        log_event(credentials.username, "admin_ingest_pdf_failed", f"filename={filename}, error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/vectordb/ingest/public/{filename}")
def ingest_public_pdf(filename: str, credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)):
    try:
        ingest.ingest_one_pdf_public(filename)
        log_event(credentials.username, "admin_ingest_public_pdf", f"filename={filename}")
        return {"detail": f"PDF '{filename}' ingested as public."}
    except Exception as e:
        log_event(credentials.username, "admin_ingest_public_pdf_failed", f"filename={filename}, error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/vectordb/ingest/private/{filename}")
def ingest_private_pdf(filename: str, user_id: str, credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)):
    try:
        ingest.ingest_one_pdf_private(filename, user_id)
        log_event(credentials.username, "admin_ingest_private_pdf", f"filename={filename}, user_id={user_id}")
        return {"detail": f"PDF '{filename}' ingested for user '{user_id}'."}
    except Exception as e:
        log_event(credentials.username, "admin_ingest_private_pdf_failed", f"filename={filename}, user_id={user_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/vectordb/pdf/{filename}")
def remove_pdf_data(filename: str, credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)):
    try:
        vectordb.clear_pdf_by_source(filename)
        log_event(credentials.username, "admin_remove_pdf_data", f"filename={filename}")
        return {"detail": f"PDF data for '{filename}' removed from vectordb."}
    except Exception as e:
        log_event(credentials.username, "admin_remove_pdf_data_failed", f"filename={filename}, error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/vectordb/pdf/user/{owner}")
def remove_pdf_data_by_user(owner: str, credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)):
    try:
        vectordb.clear_pdf_by_user(owner)
        log_event(credentials.username, "admin_remove_pdf_data_by_user", f"owner={owner}")
        return {"detail": f"All PDF data for user '{owner}' removed from vectordb."}
    except Exception as e:
        log_event(credentials.username, "admin_remove_pdf_data_by_user_failed", f"owner={owner}, error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/vectordb/pdf")
def get_available_pdf_data(credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)):
    try:
        sources = vectordb.get_pdf_sources()
        log_event(credentials.username, "admin_list_vectordb_sources", f"count={len(sources)}")
        return {"sources": sources}
    except Exception as e:
        log_event(credentials.username, "admin_list_vectordb_sources_failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/vectordb/memory")
def clear_all_users_memory(credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)):
    try:
        vectordb.clear_history_all()
        log_event(credentials.username, "admin_clear_all_users_memory", "all user chat histories cleared from vectordb")
        return {"detail": "All user chat histories cleared from vectordb."}
    except Exception as e:
        log_event(credentials.username, "admin_clear_all_users_memory_failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/vectordb/memory/{user_id}")
def clear_user_memory(user_id: str, credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)):
    try:
        vectordb.clear_history_by_user(user_id)
        log_event(credentials.username, "admin_clear_user_memory", f"user_id={user_id}")
        return {"detail": f"Chat history for user '{user_id}' cleared from vectordb."}
    except Exception as e:
        log_event(credentials.username, "admin_clear_user_memory_failed", f"user_id={user_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
