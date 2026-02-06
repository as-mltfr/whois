
from fastapi import APIRouter
from dotenv import load_dotenv
import os

load_dotenv()
router = APIRouter(prefix="/api", tags=["HOME"])

@router.get("/")
def redirect():
    return {"message": "Welcome on ASMLTFR Whois API !"}
