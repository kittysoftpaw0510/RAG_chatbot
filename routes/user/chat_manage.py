import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel
from routes.user.user_auth import verify_user_credentials
import utils.vectordb as vectordb
from utils.vectordb import save_user_message, retrieve_user_memory, retrieve_pdf_for_user
from utils.llm import LLM as chatmodel
import asyncio
from utils.logger import log_event

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@router.post("/user/chat")
async def chat(req: ChatRequest, credentials: HTTPBasicCredentials = Depends(verify_user_credentials)):
    user_id = credentials.username
    mem_docs = await asyncio.to_thread(retrieve_user_memory, user_id, req.message, 3)
    pdf_docs = await asyncio.to_thread(retrieve_pdf_for_user, user_id, req.message, 3)

    mem_text = "\n".join([d.page_content for d in mem_docs]) if mem_docs else "No previous conversation found."
    pdf_text = "\n".join([d.page_content for d in pdf_docs]) if pdf_docs else "No relevant documents found."

    await asyncio.to_thread(save_user_message, user_id, req.message)

    prompt = f"""
    Previous conversation:
    {mem_text}

    Relevant documents:
    {pdf_text}

    User: {req.message}
    Answer:
    """

    response = await asyncio.to_thread(chatmodel.predict, prompt)
    log_event(user_id, "user_chat", f"message={req.message}")
    return {"response": response, "prompt": prompt}

@router.get("/user/chat/history")
async def get_my_history(credentials: HTTPBasicCredentials = Depends(verify_user_credentials)):
    history = vectordb.get_all_history(credentials.username)
    log_event(credentials.username, "user_get_chat_history", f"count={len(history)}")
    return {"user_id": credentials.username, "history": history}
