## SMS (Simple) — FastAPI + SQLAlchemy + SQLite

### Overview
Small FastAPI service with a book scraper. Both the API and the scraper use the same database configured via `DATABASE_URL` (defaults to SQLite).

### Prerequisites
- Python 3.10+

### Quickstart
```powershell
# 1) Create a virtual environment and install deps
python -m venv venv
./venv/Scripts/python.exe -m pip install --upgrade pip
./venv/Scripts/python.exe -m pip install -r requirements.txt

# 2) Configure database (SQLite by default)
# Option A (dev default): do nothing — default is sqlite:///sms.db
# Option B: explicitly set via .env → create .env at project root with:
# DATABASE_URL=sqlite:///sms.db

# 3) Run the API
./venv/Scripts/python.exe -m uvicorn app.main:app --reload
# Open http://127.0.0.1:8000
```

### Endpoints (selected)
- POST `/students` → create student
- GET `/students/{id}` → get student
- DELETE `/students/{id}` → delete student (cascades enrollments)
- POST `/teachers` → create teacher
- DELETE `/teachers/{id}` → delete teacher (cascades teacher's courses)
- POST `/courses` → create course
- GET `/courses/{id}` → get course
- DELETE `/courses/{id}` → delete course (cascades enrollments)
- POST `/students/{id}/enroll` → enroll a student into a course
- POST `/import/scraped` → import scraped items (array of `title, link, image_url, price, scraped_at`)
- GET `/scraped_resources` → list imported scraped items
- DELETE `/scraped_resources/{id}` → delete scraped item

### Run the scraper (uses the same DATABASE_URL)
```powershell
# From project root
./venv/Scripts/python.exe scraper/scrape.py --pages 1 --db
# Produces samples/scraped.json and inserts deduped rows into scraped_resources
```

### Running tests
```powershell
# Use a separate SQLite file for tests
$env:DATABASE_URL="sqlite:///test.db"; ./venv/Scripts/python.exe -m pytest -q
```

### Configuration
- `DATABASE_URL` is read from environment or `.env`. If unset, defaults to `sqlite:///sms.db`.
- To switch databases, change `DATABASE_URL` only. Examples:
  - SQLite: `sqlite:///sms.db`
  - MySQL (optional): `mysql+pymysql://user:pass@127.0.0.1:3306/dbname?charset=utf8mb4`

### Project structure (key files)
- `app/config.py` — loads settings (DATABASE_URL)
- `app/database.py` — SQLAlchemy engine/session, table creation
- `app/models.py` — SQLAlchemy models and relationships
- `app/schemas.py` — Pydantic request/response models
- `app/crud.py` — business logic and DB operations
- `app/routes.py` — FastAPI endpoints
- `scraper/scrape.py` — book scraper, JSON output, optional DB insert
- `tests/` — API tests (pytest + httpx TestClient)

### Notes
- On Windows PowerShell, run scripts via Python: `./venv/Scripts/python.exe path\\to\\script.py`.
- If you previously used MySQL and see column errors, your old table schema may differ. With SQLite, tables are created automatically at startup.
