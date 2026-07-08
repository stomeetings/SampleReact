# Spec: Registration

## Overview
Adds user self-registration to Spendly. A visitor can submit their name, email,
and password to create an account in the existing `users` table. This is the
second backend step: it builds directly on the data layer from step 01 and
introduces the app's first HTML templates, which later steps (login, expense
CRUD) will extend.

## Depends on
- Step 01 — Database Setup (`users` table with `name`, `email` UNIQUE,
  `password_hash`, `created_at` must exist and be initialized on startup).

## Routes
- `GET /register` — render the registration form — public
- `POST /register` — validate input, create the user, redirect to success — public

## Database changes
No database changes. The existing `users` table (id, name, email UNIQUE,
password_hash, created_at) already has every column registration needs.

## Templates
- **Create:** `src/templates/base.html` — base layout (`<head>`, CSS variable
  definitions, a `{% block content %}`) that all templates extend, starting
  with this one.
- **Create:** `src/templates/register.html` — registration form (name, email,
  password fields), extends `base.html`, renders validation/duplicate-email
  errors passed from the route.
- **Create:** `src/templates/register_success.html` — simple confirmation
  page shown after successful registration, extends `base.html`.
- **Create:** `src/static/css/style.css` — CSS custom properties (colors,
  spacing) referenced by `base.html`; no hardcoded hex values in templates.

## Files to change
- `src/app.py` — import `render_template`, `request`, `redirect`, `url_for`;
  add `GET /register` and `POST /register` view functions.
- `src/database/db.py` — add `create_user(name, email, password)`: hashes the
  password with `werkzeug.security.generate_password_hash` and inserts via a
  parameterized query; lets the caller catch `sqlite3.IntegrityError` for the
  duplicate-email case (UNIQUE constraint already enforces this — no
  pre-check query needed).

## Files to create
- `src/templates/base.html`
- `src/templates/register.html`
- `src/templates/register_success.html`
- `src/static/css/style.css`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash` / never store plaintext)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Server-side validation: name, email, password required; password must be
  at least 8 characters; rely on the existing UNIQUE constraint on `email`
  for duplicate detection (catch `sqlite3.IntegrityError`, show inline error,
  do not crash)
- On success, redirect to a confirmation page — no session/cookie is created
  (login/session handling is a later step)

## Definition of done
- [ ] App starts without errors (`python src/app.py`)
- [ ] `GET /register` renders a form with name, email, password fields using `base.html`
- [ ] Submitting valid data inserts a new row into `users` with a hashed
      (non-plaintext) password, verifiable via `sqlite3 spendly.db`
- [ ] Submitting a duplicate email shows an inline error and does not insert
      a duplicate row
- [ ] Submitting with a missing field or password under 8 characters shows a
      validation error and does not insert a row
- [ ] On success, the user is redirected to `register_success.html`
- [ ] No hardcoded hex colors in any template (only CSS variables from
      `style.css`)
