# Backup

This backend service stores **JSON backups from multiple frontend applications** on a server.

Each frontend can send backup data to this service, which stores the data as JSON files in a persistent storage directory.

The service also maintains metadata in a PostgreSQL database.

Typical use cases:

- mobile app backups
- configuration backups
- user generated data
- device synchronization

---

# Badges

![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/framework-django-green)
![Docker](https://img.shields.io/badge/docker-supported-blue)
![PostgreSQL](https://img.shields.io/badge/database-postgresql-blue)
![uv](https://img.shields.io/badge/package_manager-uv-purple)

---

## Architektur
```text
Client Applications
       │
       │ HTTP / API
       ▼
Docker Container (backup)
       │
       ├── Django Application
       │       └── Gunicorn WSGI Server
       │
       ├── PostgreSQL (separate container)
       │       └── storage
       │
       └── Backup Storage
               └── /backups (host mounted volume)
```

---

## Environment variables

**HOST_IP**
- IP address or hostname of the server

**HOST_PORT**
- Port under which the server is reachable

**SECRET_KEY**
- Security key for Django.
- Must be freely chosen and remain secret.

---

## Create Dockerfile
Copy and paste the following command into your terminal to create the Dockerfile.
```bash
cat <<'EOF' > Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# TrueNAS / ZFS Fix für uv
ENV UV_LINK_MODE=copy
ENV UV_CONCURRENT_INSTALLS=1

WORKDIR /app

# uv installieren
RUN pip install --no-cache-dir uv

# Dependency Dateien zuerst kopieren
COPY pyproject.toml uv.lock ./

# Dependencies installieren
RUN uv pip install --system .

# Code kopieren
COPY . .

# Static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "300", "--keep-alive", "5"]
EOF
```

---

## Create a docker compose
Copy and paste the following command into your terminal to create the docker-compose file.
Make sure to adjust the configuration values according to your environment.
```bash
cat <<'EOF' > docker-compose.yml
version: "3.9"

services:
  backup:
    build: .
    container_name: backup
    restart: unless-stopped
    env_file:
      - .env
    ports:
      - "8000:8000"
    volumes:
      - ./backups:/backups
    networks:
      - postgres_network

networks:
  postgres_network:
    external: true
EOF

---

## Create environment
Copy and paste the following command into your terminal to create the `.env` file.
Make sure to adjust the configuration values according to your environment.
```bash
cat <<'EOF' > .env
DEBUG=False

SECRET_KEY=CHANGE_ME_TO_LONG_RANDOM_SECRET
BACKUP_TOKEN=6>K?56KmfGw8f

BACKUP_ROOT=/backups

ALLOWED_HOSTS=localhost,127.0.0.1,192.168.178.98

CORS_ALLOW_HEADERS=authorization,content-type,user-agent,x-csrftoken,x-requested-with,accept

CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000

DB_NAME=backup_db
DB_USER=backup_user
DB_PASSWORD=password
DB_HOST=postgres
DB_PORT=5432
EOF
```
