# Roblox-app VM Portal

This project runs a simple private VM portal with:
- Node API (`api`) for session management
- `websockify` for browser VNC websocket transport
- `nginx` reverse proxy for UI + API + websocket routes

## 1) Install Docker (Ubuntu)

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Log out and log back in after adding your user to `docker` group.

## 2) Prepare base VM image

```bash
sudo mkdir -p /vm-images
sudo cp /path/to/your/base.qcow2 /vm-images/base.qcow2
```

## 3) Configure environment

Edit `.env` and set a strong `APP_SECRET`.

## 4) Quick start (HTTP, no SSL)

Use this for first boot/testing:

```bash
docker compose -f docker-compose.yml -f docker-compose.http.yml up -d --build
```

Open `http://SERVER_IP/`.

## 5) Production start (HTTPS)

1. Point DNS to your server (`mehmetbatugundogan09.tech` and `www`).
2. Obtain Let's Encrypt certs on the host.
3. Start stack:

```bash
docker compose up -d --build
```

Open `https://mehmetbatugundogan09.tech/`.

## 6) Generate private access URL

```text
https://mehmetbatugundogan09.tech/api/auth/link
```

(or `http://SERVER_IP/api/auth/link` in HTTP mode)

Use the returned URL containing `?access=...`.

## 7) Logs and troubleshooting

```bash
docker compose logs -f api nginx websockify
docker compose ps
```
