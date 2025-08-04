import os
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from routes.admin import user_manage
from routes.admin import data_manage
from routes.admin import chat_manage
from routes.admin import vectordb_manage
from routes.admin import admin_auth
from routes.user import chat_manage as user_chat_manage
from routes.user import data_manage as user_data_manage
from routes.user import vectordb_manage as user_vectordb_manage
from routes.user import user_manage as user_user_manage
from routes.user import user_auth

from utils.sqlitedb import init_db

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    init_db()
    print("FastAPI Server is starting up!")
    yield
    # Shutdown code
    print("FastAPI Server is shutting down!")

app = FastAPI(lifespan=lifespan)
# Admin endpoint
app.include_router(user_manage.router)
app.include_router(data_manage.router)
app.include_router(chat_manage.router)
app.include_router(vectordb_manage.router)
app.include_router(admin_auth.router)

# User endpoint
app.include_router(user_chat_manage.router)
app.include_router(user_data_manage.router)
app.include_router(user_vectordb_manage.router)
app.include_router(user_user_manage.router)
app.include_router(user_auth.router)
