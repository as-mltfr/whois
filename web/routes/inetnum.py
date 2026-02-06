from fastapi import APIRouter, HTTPException
import requests
from dotenv import load_dotenv
import os
import urllib3

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
router = APIRouter(prefix="/api/inetnum", tags=["INETNUM"])

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

@router.get("/{inetnum}")
def get_in(inetnum: str):
    url = f"https://git.dn42/dn42/registry/raw/branch/master/data/inetnum/{inetnum}"
    token = os.getenv("REGISTRY_API_KEY")
    headers = {
        "Authorization": f"token {token}"
    }

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        return rpsl_to_json(response.text)
    else:
        raise HTTPException(status_code=response.status_code, detail="Error whith registry request.")

@router.get("/route/{inetnum}")
def get_r4(inetnum: str):
    url = f"https://git.dn42/dn42/registry/raw/branch/master/data/route/{inetnum}"
    token = os.getenv("REGISTRY_API_KEY")
    headers = {
        "Authorization": f"token {token}"
    }

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        return rpsl_to_json(response.text)
    else:
        raise HTTPException(status_code=response.status_code, detail="Error whith registry request.")