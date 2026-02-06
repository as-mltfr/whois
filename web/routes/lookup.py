from fastapi import APIRouter, HTTPException
import requests
import ipaddress
from dotenv import load_dotenv
import urllib3
import os

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
router = APIRouter(prefix="/api/lookup", tags=["AS"])

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

def prefixes_from_ip(ips):
    ip = ipaddress.ip_address(ips)
    prefixes = []
    if ip.version == 4:
        limit = ipaddress.ip_network("172.0.0.0/8")

        max_prefix = 32

        for prefix_len in range(max_prefix, 7, -1):
            net = ipaddress.ip_network(f"{ip}/{prefix_len}", strict=False)
            if net.subnet_of(limit):
                prefixes.append(net)
            else:
                break
    elif ip.version == 6:
        limit = ipaddress.ip_network("fd00::/8")

        cidr = [128, 112, 64, 56, 52, 48, 44, 40]

        for prefix_len in cidr:
            net = ipaddress.ip_network(f"{ip}/{prefix_len}", strict=False)
            if net.subnet_of(limit):
                prefixes.append(net)
            else:
                break
    return prefixes

def ipv(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

@router.get("/{ip}")
def get_as(ip: str):
    if ipv(ip):
        net = ipaddress.ip_network(ip, strict=False)
        if net.version == 4:
            prefixes = prefixes_from_ip(ip)
            asn = None
            for i, prefix in enumerate(prefixes):
                prefix = str(prefix).replace("/", "_")
                url = f"https://git.dn42/dn42/registry/raw/branch/master/data/route/{prefix}"
                print(url)
                token = os.getenv("REGISTRY_API_KEY")
                headers = {
                    "Authorization": f"token {token}"
                }

                response = requests.get(url, headers=headers, verify=False, timeout=5)

                if response.status_code == 200:
                    route = rpsl_to_json(response.text)
                    asn = route['origin']
                    break

            if asn is None:
                raise HTTPException(status_code=404, detail="IP Route not found.")

            url = f"https://git.dn42/dn42/registry/raw/branch/master/data/aut-num/{asn}"
            response = requests.get(url, headers=headers, verify=False, timeout=5)

            if response.status_code == 200:
                net = rpsl_to_json(response.text)
                netname = net['as-name']
            else:
                raise HTTPException(status_code=404, detail="Network Name not found.")
            
            return {"asn": asn, "as_name": netname}
    else:
        raise HTTPException(status_code=400, detail="Not an IP address.")
