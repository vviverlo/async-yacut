# YaCut

**URL shortener** with a web interface and REST API. Users can shorten links (with optional custom aliases) and upload files asynchronously to Yandex Disk, receiving short download links.

## Tech stack

**Backend:** Python 3.12, Flask, Flask-SQLAlchemy, Flask-WTF, asyncio, aiohttp, SQLAlchemy, pytest.

**Storage:** SQLite (default), Yandex Disk API (async file upload).

**Other:** OpenAPI specification, Postman collection.

## Key takeaways

- Built a REST API for creating and resolving short links with validation and custom aliases
- Implemented **async file uploads** to Yandex Disk using `asyncio` and `aiohttp`
- Covered the project with automated tests using pytest

## Features

- Shorten long URLs with auto-generated or custom short IDs
- REST API (`POST /api/id/`, `GET /api/id/{short_id}/`)
- Async multi-file upload to Yandex Disk with short link generation
- Web UI for link shortening and file uploads

## Getting started

### Requirements

- Python 3.12
- Yandex Disk OAuth token (for file upload feature)

### Installation

```bash
git clone https://github.com/vviverlo/async-yacut.git
cd async-yacut
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root:

```env
FLASK_APP=yacut
SECRET_KEY=your_secret_key
DATABASE_URI=sqlite:///db.sqlite3
DISK_TOKEN=your_yandex_disk_token
```

- `DATABASE_URI` — database connection string (SQLite by default)
- `DISK_TOKEN` — Yandex Disk API token (required for file uploads)

### Run the application

```bash
flask run
```

Open http://127.0.0.1:5000

### Run tests

```bash
pytest
```

## API

API specification: see `openapi.yml` in the repository root.

Example — create a short link:

```bash
curl -X POST http://127.0.0.1:5000/api/id/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/long-url"}'
```

## Author

- **Name:** Islam Ramazanov
- **Telegram:** [@arkis03](https://t.me/arkis03)
- **GitHub:** [vviverlo](https://github.com/vviverlo)
