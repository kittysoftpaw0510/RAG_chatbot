import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from routes.admin.admin_auth import verify_admin_credentials
import utils.vectordb as vectordb
from utils.logger import log_event

router = APIRouter()

@router.get("/admin/chat/history/{user_id}")
def get_chat_history(user_id: str, credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)):
    try:
        history = vectordb.get_all_history(user_id)
        log_event(credentials.username, "admin_get_chat_history", f"user_id={user_id}, count={len(history)}")
        return {"user_id": user_id, "history": history}
    except Exception as e:
        log_event(credentials.username, "admin_get_chat_history_failed", f"user_id={user_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
