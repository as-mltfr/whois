from fastapi import APIRouter, HTTPException
import requests
from dotenv import load_dotenv
import os
import urllib3

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
router = APIRouter(prefix="/api/inet6num", tags=["INET6NUM"])

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

@router.get("/{inet6num}")
def get_in(inet6num: str):
    url = f"https://git.dn42/dn42/registry/raw/branch/master/data/inet6num/{inet6num}"
    token = os.getenv("REGISTRY_API_KEY")
    headers = {
        "Authorization": f"token {token}"
    }

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        return rpsl_to_json(response.text)
    else:
        raise HTTPException(status_code=response.status_code, detail="Error whith registry request.")

@router.get("/route/{inet6num}")
def get_r6(inet6num: str):
    url = f"https://git.dn42/dn42/registry/raw/branch/master/data/route6/{inet6num}"
    token = os.getenv("REGISTRY_API_KEY")
    headers = {
        "Authorization": f"token {token}"
    }

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        return rpsl_to_json(response.text)
    else:
        raise HTTPException(status_code=response.status_code, detail="Error whith registry request.")