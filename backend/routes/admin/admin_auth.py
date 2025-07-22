import os
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from utils.logger import log_event

security = HTTPBasic()
router = APIRouter()

def verify_admin_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.environ.get("ADMIN_USERNAME", "admin")
    correct_password = os.environ.get("ADMIN_PASSWORD", "123123")
    if credentials.username != correct_username or credentials.password != correct_password:
        log_event(credentials.username, "admin_auth_check", "failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    log_event(credentials.username, "admin_auth_check", "success")
    return credentials

@router.get("/admin/auth/check")
def admin_auth_check(credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)):
    return {"detail": "Admin authentication successful."}
