# Plan: Implement SQLite Database Layer (Spendly)

## Context

`.claude/Specs/01-database_setup.md` defines the first backend step for the Spendly expense-tracker app: a working SQLite data layer in `src/database/db.py`, wired into `src/app.py` on startup. This is the foundation every future feature (auth, profile, expense tracking) depends on.

Both `src/database/db.py` and `src/app.py` existed as **empty files** (0 bytes) before this change — this was a fully greenfield Python backend with no Flask app, no `requirements.txt`, and no venv in the repo. The spec assumes an existing Flask `app` instance to attach `init_db()`/`seed_db()` to via `app.app_context()`, so this plan also creates a minimal Flask skeleton in `app.py` (not just the two lines the spec literally shows) so the wiring has something real to attach to.

Note: the spec says "no new pip packages" and treats Flask/werkzeug as already installed. Since nothing was installed in this repo, this plan adds a minimal `requirements.txt` (`Flask`, which pulls in `Werkzeug`) so `pip install -r requirements.txt` works — this is a necessary addition to make the spec's assumption true, not scope creep.

## Files changed/created

- **`src/database/db.py`** — implemented fully (was empty stub)
- **`src/app.py`** — minimal Flask app + startup wiring (was empty stub)
- **`requirements.txt`** (new, project root) — `Flask` only

## 1. `src/database/db.py`

```python
import sqlite3
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

DB_PATH = "spendly.db"

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    existing = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
    if existing["count"] > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cursor.lastrowid

    today = date.today()
    sample_expenses = [
        (user_id, 45.50, "Food", (today - timedelta(days=1)).isoformat(), "Groceries"),
        (user_id, 12.00, "Transport", (today - timedelta(days=2)).isoformat(), "Bus fare"),
        (user_id, 89.99, "Bills", (today - timedelta(days=3)).isoformat(), "Electricity"),
        (user_id, 30.00, "Health", (today - timedelta(days=4)).isoformat(), "Pharmacy"),
        (user_id, 15.00, "Entertainment", (today - timedelta(days=5)).isoformat(), "Movie ticket"),
        (user_id, 60.00, "Shopping", (today - timedelta(days=6)).isoformat(), "Clothes"),
        (user_id, 8.75, "Other", (today - timedelta(days=7)).isoformat(), "Misc"),
        (user_id, 22.30, "Food", (today - timedelta(days=8)).isoformat(), "Restaurant"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        sample_expenses,
    )
    conn.commit()
    conn.close()
```

Key points from the spec this must satisfy:
- `get_db()`: `sqlite3.Row` row factory, `PRAGMA foreign_keys = ON`, returns the connection.
- `init_db()`: `CREATE TABLE IF NOT EXISTS` for both tables, safe to call repeatedly.
- `seed_db()`: early-returns if `users` already has rows (no duplicate seeding); inserts the demo user with a `werkzeug`-hashed password; inserts exactly 8 expenses covering all 7 categories, dated across the current month, all FK'd to the demo user.
- All queries parameterized (`?` placeholders) — no string formatting into SQL, per spec rule.
- `amount` stored as REAL; `date`/`created_at` as `YYYY-MM-DD` / `datetime('now')` text.

## 2. `src/app.py`

Minimal Flask skeleton plus the spec's required startup wiring:

```python
from flask import Flask
from database.db import get_db, init_db, seed_db

app = Flask(__name__)

with app.app_context():
    init_db()
    seed_db()


@app.route("/")
def index():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
```

- Imports `get_db`, `init_db`, `seed_db` as the spec requires (even though `get_db` isn't called directly here — routes added in later steps will use it).
- Calls `init_db()` and `seed_db()` inside `app.app_context()` at startup, before any routes handle requests.
- The `/` route and `if __name__ == "__main__"` block are the minimal scaffold needed to make this a runnable Flask app.

## 3. `requirements.txt` (new)

```
Flask
```

(`Werkzeug` is a transitive dependency of Flask, satisfying the spec's `werkzeug.security` requirement without a separate line.)

## Verification

1. `pip install -r requirements.txt` (in the repo's Python environment).
2. `python src/app.py` — confirm it starts without errors and `spendly.db` is created in the working directory.
3. Inspect the DB (`sqlite3 spendly.db` or a quick Python snippet) and confirm:
   - `users` table has exactly 1 row (Demo User, hashed password, unique email).
   - `expenses` table has exactly 8 rows, all `user_id` = demo user's id, categories cover all 7 values, dates in `YYYY-MM-DD`.
4. Re-run `python src/app.py` a second time — confirm no duplicate rows are inserted (`seed_db()` idempotency) and no errors on `init_db()` re-running `CREATE TABLE IF NOT EXISTS`.
5. Manually test constraint enforcement:
   - Attempt inserting a second user with `email = "demo@spendly.com"` → should raise `sqlite3.IntegrityError` (UNIQUE).
   - Attempt inserting an expense with a nonexistent `user_id` → should raise `sqlite3.IntegrityError` (FOREIGN KEY), confirming `PRAGMA foreign_keys = ON` took effect.
