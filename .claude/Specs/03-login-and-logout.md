# Spec: Login and Logout

## Overview
Adds session-based authentication to Spendly. Registered users (created via
the step-02 `/register` flow) can now log in with their email and password,
and log out to end their session. This is the first step in the roadmap
that introduces `flask.session`, laying the groundwork for future steps
that will gate expense-tracking pages behind a logged-in check.

## Depends on
- Step 01 (database setup) — `users` table and `get_db()`.
- Step 02 (registration) — users must be able to register before they can
  log in; reuses the same `users` table and no new columns.

## Routes
- `GET /login` — render the login form — public (already-logged-in users are
  redirected to `/login/success`)
- `POST /login` — validate credentials, create session on success — public
- `GET /login/success` — confirmation page shown after a successful login — logged-in
- `GET /logout` — clear the session, redirect to `/login` — logged-in

Already-logged-in users are also redirected away from `/register` (to
`/login/success`), since there's nothing for a logged-in user to do there.

## Database changes
No new tables or columns. Adds one new read function to
`src/database/db.py`:
- `get_user_by_email(email)` — parameterized `SELECT * FROM users WHERE
  email = ?`, returns the row (including `password_hash`) or `None`.

## Templates
- **Create:**
  - `src/templates/login.html` — email/password form, mirrors
    `register.html`'s structure (inline `{{ errors.field }}` spans,
    repopulates `form.email` on failure), posts to `url_for('login')`.
  - `src/templates/login_success.html` — mirrors `register_success.html`;
    shows "Welcome back, {{ name }}" and a logout link.
- **Modify:**
  - `src/templates/base.html` — add a small nav conditional: show
    "Login" / "Register" links when `session` has no `user_id`, or the
    user's name + a "Logout" link when it does.
  - `src/templates/register_success.html` — update the existing line
    ("You can log in once the login feature is available.") to link to
    `url_for('login')` now that the route exists.

## Files to change
- `src/app.py` — set `app.secret_key`, add `login`/`login_success`/`logout`
  view functions, import `check_password_hash` and `get_user_by_email`.
- `src/database/db.py` — add `get_user_by_email(email)`.
- `src/templates/base.html` — nav conditional (see above).
- `src/templates/register_success.html` — update login link text.

## Files to create
- `src/templates/login.html`
- `src/templates/login_success.html`

## New dependencies
No new dependencies — uses Flask's built-in signed-cookie `session` and
Werkzeug's `check_password_hash`, both already available transitively via
the existing `Flask` dependency.

## Rules for implementation
- No SQLAlchemy or ORMs.
- Parameterized queries only.
- Passwords verified with `werkzeug.security.check_password_hash` — never
  compare plaintext.
- `app.secret_key` must come from `os.environ.get("SECRET_KEY", <dev
  fallback>)`, not a bare hardcoded string, so it isn't a real secret
  shipped in source.
- On failed login, show one generic "Invalid email or password" message —
  never reveal whether the email or the password was the wrong part
  (avoids user enumeration).
- Use CSS variables — never hardcode hex values.
- All templates extend `base.html`.

## Definition of done
- [ ] Visiting `/login` shows a form with email and password fields.
- [ ] Submitting the seeded demo credentials (`demo@spendly.com` /
      `demo123`) logs in and redirects to `/login/success`, which displays
      "Welcome back, Demo User".
- [ ] Submitting a wrong password or unknown email shows the generic
      "Invalid email or password" error and repopulates the email field.
- [ ] After logging in, the base template nav shows a "Logout" link instead
      of "Login"/"Register".
- [ ] Visiting `/logout` clears the session and redirects to `/login`,
      after which the nav reverts to "Login"/"Register".
- [ ] `register_success.html`'s login link points to `/login` and works.
- [ ] `get_user_by_email` uses a parameterized query (no string
      interpolation into SQL).
- [ ] While logged in, visiting `/login` or `/register` redirects to
      `/login/success` instead of showing the form.
