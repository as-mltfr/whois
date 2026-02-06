import socket
import threading
import requests
import ipaddress
from dotenv import load_dotenv
import os
import re
import urllib3

#  __          ___    _  ____ _____  _____ _  _ ___                                 
#  \ \        / / |  | |/ __ \_   _|/ ____| || |__ \                                
#   \ \  /\  / /| |__| | |  | || | | (___ | || |_ ) |  ___  ___ _ ____   _____ _ __ 
#    \ \/  \/ / |  __  | |  | || |  \___ \|__   _/ /  / __|/ _ \ '__\ \ / / _ \ '__|
#     \  /\  /  | |  | | |__| || |_ ____) |  | |/ /_  \__ \  __/ |   \ V /  __/ |   
#      \/  \/   |_|  |_|\____/_____|_____/   |_|____| |___/\___|_|    \_/ \___|_|   
#
# Made by MLTFR for DN42.  

# Verifying if connected on DN42
param = '-n 1 -w 1000' if os.sys.platform.lower()=='win32' else '-c 1 -W 1'

# IPv6
test = os.system(f"ping -6 {param} git.dn42")
if test != 0:
    test = os.system(f"ping -4 {param} git.dn42")
rega = 'git.dn42' if test == 0 else 'git.dn42.dev'

# Loading env file
if os.path.exists(".env"):
    load_dotenv()
else:
    raise ".env file not found"

# Disabling SSL errors
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Functions
def prefixes_from_ip(ip_str):
    """
    Docstring for prefixes_from_ip:

    Input: ip (string)
    Output: prefixes (list)

    This function return every prefixes which an IP can be apart of.
    """

    ip = ipaddress.ip_address(ip_str)
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


def ip(query):
    """
    Docstring for ipv:
    
    Input: query (string)
    Output: boolean value

    This function return if the query is an IP.
    """

    try:
        ipaddress.ip_address(query)
        return True
    except ValueError:
        return False

def search(query: str):
    """
    Docstring for search:
    
    Input: query (string)
    Ouput: response (string)
    """

    query = query.strip()

    if re.fullmatch(r"AS(\d+)", query, re.IGNORECASE) or query.isdigit():
        if not query.isdigit():
            asn = int(query[2:])
        else:
            asn = int(query)
        if 65000 <= asn <= 4242429999:
            url = f"https://{rega}/dn42/registry/raw/branch/master/data/aut-num/AS{asn}"
            token = os.getenv("REGISTRY_API_KEY")
            headers = {
                "Authorization": f"token {token}"
            }

            response = requests.get(url, headers=headers, verify=False, timeout=5)

            if response.status_code == 200:
                rep = f"% Information related to 'aut-num/AS{asn}':\n"
                rep += response.text
                return rep
            elif response.status_code == 404:
                return "% No entries found.\n"
            else:
                return "% An error occured while asking registry.\n"
        else:
            return "% Not in DN42 range.\n"
    elif "/" in query or "_" in query:
        net = ipaddress.ip_network(query, strict=False)
        if "/" in query:
            p = query.replace("/", "_")
        else:
            p = query
        if net.version == 6:
            url = f"https://{rega}/dn42/registry/raw/branch/master/data/inet6num/{p}"
            token = os.getenv("REGISTRY_API_KEY")
            headers = {
                "Authorization": f"token {token}"
            }

            response = requests.get(url, headers=headers, verify=False, timeout=5)

            if response.status_code == 200:
                rep = f"% Information related to 'inet6num/{p}':\n"
                rep += response.text
                rep += f"\n\n% Information related to 'route6/{p}':\n"

                url = f"https://{rega}/dn42/registry/raw/branch/master/data/route6/{p}"
                token = os.getenv("REGISTRY_API_KEY")
                headers = {
                    "Authorization": f"token {token}"
                }

                response = requests.get(url, headers=headers, verify=False, timeout=5)

                if response.status_code == 200:
                    rep += response.text
                    return rep
                elif response.status_code == 404:
                    return "% No entries found.\n"
                else:
                    return "% An error occured while asking registry.\n"
            elif response.status_code == 404:
                return "% No entries found.\n"
            else:
                return "% An error occured while asking registry.\n"
        elif net.version == 4:
            url = f"https://{rega}/dn42/registry/raw/branch/master/data/inetnum/{p}"
            token = os.getenv("REGISTRY_API_KEY")
            headers = {
                "Authorization": f"token {token}"
            }

            response = requests.get(url, headers=headers, verify=False, timeout=5)

            if response.status_code == 200:
                rep = f"% Information related to 'inet-num/{p}':\n"
                rep += response.text
                rep += f"\n\n% Information related to 'route/{p}':\n"

                url = f"https://{rega}/dn42/registry/raw/branch/master/data/route/{p}"
                token = os.getenv("REGISTRY_API_KEY")
                headers = {
                    "Authorization": f"token {token}"
                }

                response = requests.get(url, headers=headers, verify=False, timeout=5)

                if response.status_code == 200:
                    rep += response.text
                    return rep
                elif response.status_code == 404:
                    return "% No entries found.\n"
                else:
                    return "% An error occured while asking registry.\n"
            elif response.status_code == 404:
                return "% No entries found.\n"
            else:
                return "% An error occured while asking registry.\n"
        else:
            return "% Error 418: I'm a teapot."
    elif query[-5:] == ".dn42":
        parts = query.strip('.').lower().split('.')
        fqdn = query
        if len(parts) > 2:
            fqdn = ".".join(parts[-2:])
        else:
            fqdn = query

        url = f"https://{rega}/dn42/registry/raw/branch/master/data/dns/{fqdn}"
        token = os.getenv("REGISTRY_API_KEY")
        headers = {
            "Authorization": f"token {token}"
        }

        response = requests.get(url, headers=headers, verify=False, timeout=5)

        if response.status_code == 200:
            rep = f"% Information related to 'dns/{fqdn}':\n"
            rep += response.text
            return rep
        elif response.status_code == 404:
            return "% No entries found.\n"
        else:
            return "% An error occured while asking registry.\n"
    elif query.upper().endswith("-MNT"):
        query = query.upper()
        url = f"https://{rega}/dn42/registry/raw/branch/master/data/mntner/{query}"
        token = os.getenv("REGISTRY_API_KEY")
        headers = {
            "Authorization": f"token {token}"
        }

        response = requests.get(url, headers=headers, verify=False, timeout=5)

        if response.status_code == 200:
            rep = f"% Information related to 'mntner/{query}':\n"
            rep += response.text
            return rep
        elif response.status_code == 404:
            return "% No entries found.\n"
        else:
            return "% An error occured while asking registry.\n"
    elif query.upper().endswith("-DN42"):
        query = query.upper()
        url = f"https://{rega}/dn42/registry/raw/branch/master/data/person/{query}"
        token = os.getenv("REGISTRY_API_KEY")
        headers = {
            "Authorization": f"token {token}"
        }

        response = requests.get(url, headers=headers, verify=False, timeout=5)

        if response.status_code == 200:
            rep = f"% Information related to 'person/{query}':\n"
            rep += response.text
            return rep
        elif response.status_code == 404:
            return "% No entries found.\n"
        else:
            return "% An error occured while asking registry.\n"
    elif ip(query):
        net = ipaddress.ip_network(query, strict=False)
        if net.version == 4:
            prefixes = prefixes_from_ip(query)
            for i, prefix in enumerate(prefixes_from_ip(query)):
                prefix = str(prefix).replace("/", "_")
                print(prefix)
                url = f"https://{rega}/dn42/registry/raw/branch/master/data/route/{prefix}"
                token = os.getenv("REGISTRY_API_KEY")
                headers = {
                    "Authorization": f"token {token}"
                }

                response = requests.get(url, headers=headers, verify=False, timeout=5)

                if response.status_code == 200:
                    rep = f"% Information related to 'route/{query}':\n"
                    rep += response.text

                    url = f"https://{rega}/dn42/registry/raw/branch/master/data/inetnum/{prefix}"
                    token = os.getenv("REGISTRY_API_KEY")
                    headers = {
                        "Authorization": f"token {token}"
                    }

                    response = requests.get(url, headers=headers, verify=False, timeout=5)

                    if response.status_code == 200:
                        rep += f"\n\n% Information related to 'inetnum/{query}':\n"
                        rep += response.text
                        return rep
                    elif response.status_code == 404:
                        rep += "% No inetnum object found.\n"
                        return rep
                    else:
                        rep += "% An error occured while asking registry for inetnum object.\n"
                        return rep
                elif response.status_code == 404:
                    if i == len(prefixes) - 1:
                        return "% No entries found.\n"
                else:
                    if i == len(prefixes) - 1:
                        return "% An error occured while asking registry.\n"
        elif net.version == 6:
            prefixes = prefixes_from_ip(query)
            for i, prefix in enumerate(prefixes_from_ip(query)):
                prefix = str(prefix).replace("/", "_")
                print(prefix)
                url = f"https://{rega}/dn42/registry/raw/branch/master/data/route6/{prefix}"
                token = os.getenv("REGISTRY_API_KEY")
                headers = {
                    "Authorization": f"token {token}"
                }

                response = requests.get(url, headers=headers, verify=False, timeout=5)

                if response.status_code == 200:
                    rep = f"% Information related to 'route6/{query}':\n"
                    rep += response.text

                    url = f"https://{rega}/dn42/registry/raw/branch/master/data/inet6num/{prefix}"
                    token = os.getenv("REGISTRY_API_KEY")
                    headers = {
                        "Authorization": f"token {token}"
                    }

                    response = requests.get(url, headers=headers, verify=False, timeout=5)

                    if response.status_code == 200:
                        rep += f"\n\n% Information related to 'inet6num/{query}':\n"
                        rep += response.text
                        return rep
                    elif response.status_code == 404:
                        rep += "% No inetnum object found.\n"
                        return rep
                    else:
                        rep += "% An error occured while asking registry for inetnum object.\n"
                        return rep
                elif response.status_code == 404:
                    if i == len(prefixes) - 1:
                        return "% No entries found.\n"
                else:
                    if i == len(prefixes) - 1:
                        return "% An error occured while asking registry.\n"
    return None

def handle_client(conn: socket.socket, addr: tuple):
    """
    Docstring for handle_client:

    Input: conn (socket.socket), addr(tuple)
    
    This function handle client connection while answering the registry.
    """

    try:
        query = conn.recv(1024).decode('utf-8').strip()
        print(f"[{addr[0]}] Request: {query}")
        response = "% This is a WHOIS server from AS-MLTFR Network for DN42 network.\n% Code available on: https://git.asmltfr.dn42/asmltfr/whois-server.\n% Web interface: https://whois.asmltfr.dn42/.\n\n"
        results = search(query)
        if isinstance(results, str):
            response += results
        else:
            response += "% No entries found.\n"
        conn.sendall(response.encode('utf-8'))
    except Exception as e:
        print(f"[!] ERROR: {e}")
    finally:
        conn.close()

def start_server(host='0.0.0.0', port=43):
    """
    Docstring for start_server:

    Input: host (string), port (integer)

    This function manage the whois server.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(10)
        s.settimeout(1.0)
        print(f"Server listening on {host}:{port}")

        try:
            while True:
                try:
                    conn, addr = s.accept()
                    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            print("\nStopping server.")

if __name__ == "__main__":
    start_server()