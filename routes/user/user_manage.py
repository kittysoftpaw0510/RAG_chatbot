import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import utils.sqlitedb as db
from utils.logger import log_event

router = APIRouter()

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/user/login")
def user_login(user: UserLogin):
    if db.authenticate_user(user.username, user.password):
        log_event(user.username, "user_login", "success")
        return {"success": True, "user_id": user.username}
    else:
        log_event(user.username, "user_login", "failed")
        raise HTTPException(status_code=401, detail="Invalid username or password.") 