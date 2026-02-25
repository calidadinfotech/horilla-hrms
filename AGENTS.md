# Horilla HRMS

Horilla is a Django-based open-source HRMS (Human Resource Management System). See `README.md` for full installation and feature documentation.

## Cursor Cloud specific instructions

### Project overview

Single Django monolith serving web UI + REST API on port 8000. Uses SQLite by default for development (no external DB required). All HR modules (employee, recruitment, leave, attendance, payroll, etc.) are Django apps within this repo.

### Running the dev server

```bash
source /workspace/venv/bin/activate
python3 manage.py runserver 0.0.0.0:8000
```

The `.env` file is already configured for SQLite development. If the DB is fresh, run migrations first:

```bash
python3 manage.py makemigrations && python3 manage.py migrate
```

After migrations, visit `http://localhost:8000` and use "Initialize Database" with password from `.env` (`DB_INIT_PASSWORD`) to create the super admin, company, department, and job position. Admin credentials: `admin` / `Admin@123`.

### Linting

The project uses `black` and `isort` (with `--profile black`). Both are installed in the virtualenv:

```bash
black --check .
isort --check-only --profile black .
```

Pre-commit hooks are defined in `.pre-commit-config.yaml` (black, isort, trailing-whitespace, end-of-file-fixer, check-yaml).

### Translations

Compile translation files (requires `gettext` system package):

```bash
python3 manage.py compilemessages
```

### Gotchas

- The `makemigrations` step generates migration files for several app modules (horilla_audit, horilla_views, accessibility, etc.) that don't have pre-committed migrations. This is normal — these are generated dynamically via `horilla_apps.py`.
- A harmless warning appears at startup: `Could not start automation: no such table: horilla_automations_mailautomation` — this resolves after `migrate` runs.
- The `requests` library produces a `RequestsDependencyWarning` about urllib3/chardet version mismatch — this is cosmetic and does not affect functionality.
- Django settings default to SQLite when no `DATABASE_URL` or `DB_ENGINE` is set in `.env`. For development, this is the simplest path.
- Static files are pre-built in `static/`. Node.js / `npm run dev` (Laravel Mix) is only needed if modifying SCSS/JS source files.
