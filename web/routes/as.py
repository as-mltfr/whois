from fastapi import APIRouter, HTTPException
import requests
from dotenv import load_dotenv
import urllib3

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
router = APIRouter(prefix="/api/as", tags=["AS"])

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

@router.get("/{asn}")
def get_as(asn: int):
    url = f"https://git.dn42/dn42/registry/raw/branch/master/data/aut-num/AS{asn}"
    token = "83cc5688a852a8d8e9e7b213c9576a882bf575b9"
    headers = {
        "Authorization": f"token {token}"
    }

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        return rpsl_to_json(response.text)
    else:
        raise HTTPException(status_code=response.status_code, detail="Error whith registry request.")