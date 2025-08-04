import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from routes.user.user_auth import verify_user_credentials
import utils.ingest as ingest
import utils.vectordb as vectordb
from utils.sqlitedb import get_ingested_pdfs_by_user, delete_ingested_pdf_by_id
from utils.logger import log_event

router = APIRouter()

@router.post("/user/vectordb/ingest/all")
def ingest_all(credentials: HTTPBasicCredentials = Depends(verify_user_credentials)):
    try:
        ingest.ingest_my_all_pdfs(user_id=credentials.username)
        log_event(credentials.username, "user_ingest_all_pdfs", "all user PDFs ingested")
        return {"detail": "All your PDFs ingested."}
    except Exception as e:
        log_event(credentials.username, "user_ingest_all_pdfs_failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user/vectordb/ingest/one/{filename}")
def ingest_by_filename(filename: str, credentials: HTTPBasicCredentials = Depends(verify_user_credentials)):
    try:
        ingest.ingest_one_pdf_user(filename, user_id=credentials.username)
        log_event(credentials.username, "user_ingest_pdf", f"filename={filename}")
        return {"detail": f"PDF '{filename}' ingested."}
    except Exception as e:
        log_event(credentials.username, "user_ingest_pdf_failed", f"filename={filename}, error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user/vectordb/pdf/one/{filename}")
def remove_pdf_data(filename: str, credentials: HTTPBasicCredentials = Depends(verify_user_credentials)):
    try:
        vectordb.clear_pdf_by_source_userid(filename, credentials.username)
        log_event(credentials.username, "user_remove_pdf_data", f"filename={filename}")
        return {"detail": f"PDF data for '{filename}' removed from vectordb."}
    except Exception as e:
        log_event(credentials.username, "user_remove_pdf_data_failed", f"filename={filename}, error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user/vectordb/pdf/all")
def remove_all_pdf_data(credentials: HTTPBasicCredentials = Depends(verify_user_credentials)):
    try:
        vectordb.clear_pdf_by_user(credentials.username)
        ingested = get_ingested_pdfs_by_user(credentials.username)
        for pdf in ingested:
            delete_ingested_pdf_by_id(pdf["id"])
        log_event(credentials.username, "user_remove_all_pdf_data", "all user PDF data removed from vectordb")
        return {"detail": "All your PDF data removed from vectordb."}
    except Exception as e:
        log_event(credentials.username, "user_remove_all_pdf_data_failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/vectordb/pdf")
def get_available_pdf_data(credentials: HTTPBasicCredentials = Depends(verify_user_credentials)):
    try:
        sources = vectordb.get_pdf_sources()
        filtered = [s for s in sources if s["ingested_by"] == credentials.username or s["ingested_by"] == "public"]
        log_event(credentials.username, "user_list_vectordb_sources", f"count={len(filtered)}")
        return {"sources": filtered}
    except Exception as e:
        log_event(credentials.username, "user_list_vectordb_sources_failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user/vectordb/memory")
def clear_my_memory(credentials: HTTPBasicCredentials = Depends(verify_user_credentials)):
    try:
        vectordb.clear_history_by_user(credentials.username)
        log_event(credentials.username, "user_clear_memory", "chat history cleared from vectordb")
        return {"detail": "Your chat history cleared from vectordb."}
    except Exception as e:
        log_event(credentials.username, "user_clear_memory_failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))
