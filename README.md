# ASMLTFR WHOIS Tool

A web UI + REST API + WHOIS Server to interact with DN42 registry in real time.

---

## 🛰️ Features

- Responsive web interface (HTML + Bootstrap)
- Real-time WHOIS lookup via web form
- REST API using python FastAPI, including a "proxy" to connect UI with WHOIS
- Supports IPv4, IPv6, domains and ASNs.

## 🚀  Usage

### Web UI

Just enter an IP prefix (v4 or v6), an ASN, or a domain in the input field.
Valid exemples:

- `172.20.18.240/28`
- `fd8b:dc6c:8653::/48`
- `asmltfr.dn42`
- `as4242422412`

### WHOIS CLI Usage

Query directly via port 43:

```bash
whois -h whois.domain.dn42 fd8b:dc6c:8653::/48
```

### REST API

Use a simple HTTP request format:
```bash
GET http://whois.yourserver.dn42/{type}/{object}
```

Examples:
```bash
GET http://whois.yourserver.dn42/inetnum/172.20.18.240/28 # inet6num for IPv6
GET http://whois.yourserver.dn42/route/172.20.18.240/28 # route6 for IPv6
GET http://whois.yourserver.dn42/domain/asmltfr.dn42
GET http://whois.yourserver.dn42/aut-num/4242422412
```

### API Proxy

To help the web UI to request the WHOIS server you need to configure a proxy between the UI and the WHOIS server. The proxy is installed on the API.

You can query the WHOIS server with your REST API like that:
```bash
GET http://whois.yourserver.dn42/api/whois/<object>
```

## Installation

## Cloning repo

Clone the repo:
```bash
sudo git clone http://git.asmltfr.dn42/mltfr/whois.git
sudo mkdir /opt/whois/
sudo mv whois/* /opt/whois/
```

**Now, we're going to configure the WHOIS server.**

## WHOIS Server

Configure env variables:
```bash
cd /opt/whois/server
sudo mv .env.example .env
```

And replace ``str`` by your api key.
You can generate one here: https://git.dn42.dev/user/settings/applications (Clearnet); https://git.dn42/user/settings/applications (DN42) and click on "Generate a new token".
Add this permissions:
*Access to Organizations and Repositories*: Public only
| Permission   | Access    |
|--------------|-----------|
| activitypub  | No access |
| issue        | No access |
| misc         | No access |
| notification | No access |
| organization | No access |
| package      | No access |
| repository   | Read      |
| user         | No access |

Create a process:
```bash
sudo nano /etc/systemd/system/whois-server.service
```

```service
[Unit]
Description=WHOIS Server
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/whois/server
ExecStart=/your/directory/to/python3 main.py # Often /usr/local/lib/python<version>
Restart=always

[Install]
WantedBy=multi-user.target
```
You need to run the server as root or superadmin due to port 43.

And activate it:
```bash
sudo systemctl daemon-reload
sudo systemctl enable whois-server --now
```

**Congratulations ! Your WHOIS server is now configured.**

You can test it by executing the following command:
```bash
sudo apt install whois -y
whois -h <your_ip> <object>
```

## API

Go to the API repo:
```bash
cd /opt/whois/api
```

Configure a virtual environment for python:
```bash
sudo apt install python3.11-venv
sudo python3 venv venv
source venv/bin/ctivate
pip install -r requirements.txt
```

Configure env variables:
```bash
sudo mv .env.example .env
sudo nano .env
```
Change ``REGISTRY_API_KEY=*str*`` by your DN42 Gitea Token, ``WHOIS_ADDR=*str*`` by your WHOIS server ip and ``WHOIS_PORT`` by your WHOIS server port (usually 43) and ``WEB_UI_URL=str`` by your WHOIS web url.

Create a process:
```bash
sudo nano /etc/systemd/system/whois-api.service
```
```service
[Unit]
Description=WHOIS API
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/whois/api
ExecStart=/opt/whois/venv/bin/gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Activate it:
```bash
sudo systemctl daemon-reload
sudo systemctl enable whois-api --now
```

Your API is now running.

## Web UI

Install NGINX:
```bash
sudo apt install nginx -y
```

Configure a nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/whois
```
```bash
server {
    listen 80;
    server_name whois.domain.dn42;

    root /opt/whois/web/;
    index index.html; 

    location / {
        try_files $uri $uri/ =404;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Verify and restart NGINX:
```bash
sudo ln -s /etc/nginx/sites-available/whois /etc/nginx/sites-enabled/whois
sudo nginx -t
sudo systemctl restart nginx
```

Now your Web UI is online, you can access to your API by calling: ``whois.domain.dn42/api/``, if it redirects you to ``whois.domain.dn42/`` the API is working !

You now have a complete WHOIS system online.