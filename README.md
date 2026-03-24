# Backup

This backend service stores **JSON backups from multiple frontend applications** on a server.

Each frontend can send backup data to this service, which stores the data as JSON files in a persistent storage directory.

Built with:

- **Django / Django REST** – Backend and API
- **PostgreSQL** – Persistent database
- **Docker** – Containerized deployment
- **uv** – Python dependency manager

---

# Badges

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-framework-092E20?logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-supported-2496ED?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-4169E1?logo=postgresql&logoColor=white)
![uv](https://img.shields.io/badge/package_manager-uv-purple)
![JavaScript](https://img.shields.io/badge/JavaScript-language-F7DF1E?logo=javascript&logoColor=black)
![HTML](https://img.shields.io/badge/HTML-markup-E34F26?logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-style-1572B6?logo=css3&logoColor=white)
![License](https://img.shields.io/badge/license-all_rights_reserved-red)

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

## Security Notice

Do **NOT** commit the following files:

.env

/backups


The **.env** file contains secrets such as:

SECRET_KEY, BACKUP_TOKEN, DATABASE_PASSWORD

---

## Create Dockerfile
Copy and paste the following command into your terminal to create the Dockerfile.
```bash
cat <<'EOF' > Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ZFS Fix für uv
ENV UV_LINK_MODE=copy
ENV UV_CONCURRENT_INSTALLS=1

WORKDIR /app

# uv installieren
RUN pip install --no-cache-dir uv

# Dependency Dateien kopieren
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
      - "${HOST_PORT}:8000"
    volumes:
      - ./backups:/backups
    networks:
      - postgres_network

networks:
  postgres_network:
    external: true
EOF
```

---

## Create environment
Copy and paste the following command into your terminal to create the `.env` file.
Make sure to adjust the configuration values according to your environment. **.env** should never be committed to git.
```bash
cat <<'EOF' > .env
DEBUG=False

SECRET_KEY=CHANGE_ME_TO_LONG_RANDOM_SECRET
BACKUP_TOKEN=CHANGE_ME

BACKUP_ROOT=/backups

ALLOWED_HOSTS=localhost,127.0.0.1,<HOST_IP>
CORS_ALLOW_HEADERS=authorization,content-type,user-agent,x-csrftoken,x-requested-with,accept

CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000

DB_NAME=backup_db
DB_USER=backup_user
DB_PASSWORD=CHANGE_ME
DB_HOST=postgres
DB_PORT=5432

SUPERUSER_USERNAME=admin
SUPERUSER_PASSWORD=admin123
SUPERUSER_EMAIL=admin@example.com
EOF
```

---

## Execute migration
```bash
sudo docker exec -it backup python manage.py makemigrations
sudo docker exec -it backup python manage.py migrate
```

**makemigration** analyzes changes in the Django models and creates migration files.

**migrate** executes the created migrations in the database.

---

## create superuser
```bash
sudo docker compose exec backup python manage.py seed_users
```
---

## Static sammeln
```bash
sudo docker exec -it backup python manage.py collectstatic
```

---

## Open web gui
The backend provides a simple web interface to manage stored backups.
```bash
http://HOST_IP:HOST_PORT/gui/
```

## License

This project is not open source.

All rights reserved.

The source code is provided for viewing purposes only.

You are not permitted to:

- copy the code
- reuse the code
- redistribute the code
- use the code commercially
