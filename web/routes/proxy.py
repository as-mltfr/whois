
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
import socket
from dotenv import load_dotenv
import os

load_dotenv()
router = APIRouter(prefix="/api/whois", tags=["WHOIS"])

def rpsl_to_json(rpsl_text: str) -> dict:
    data = {}
    for line in rpsl_text.strip().split("\n"):
        if not line.strip():
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data

@router.get("/{object:path}")
def rew_whois(object: str):
    host = os.getenv("WHOIS_ADDR")
    port = os.getenv("WHOIS_PORT")

    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            sock.sendall((object + "\r\n").encode("utf-8"))
            response = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data
        return PlainTextResponse(response.decode('utf-8'))
    except Exception as e:
        raise HTTPException(500, "An error occurred while asking WHOIS server.")
