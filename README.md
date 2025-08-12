# Personal Account Manager

A minimal FastAPI application for managing accounts, contacts, tasks, notes, and attachments. This project is intended for local use and serves as the foundation for a more feature-complete web app.

## Development Setup

1. Open your terminal and run these commands to copy the project to your computer:
   ```bash
   git clone https://github.com/curlyphries/Personal-Account-Manager.git
   cd Personal-Account-Manager
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv        # create venv
   source .venv/bin/activate    # activate (use `.venv\Scripts\activate` on Windows)
   ```
   When finished, exit the environment:
   ```bash
   deactivate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`. A basic health check lives at the root endpoint.
Navigate to `/ui` in your browser for a minimal web interface to manage accounts.

### Environment Variables

- `DATABASE_URL` – connection string for the database. Defaults to a local SQLite database at `data/app.db`.
- `DEBUG` – set to `1` to enable SQLModel's SQL echo for debugging.

### Running Tests

Execute the test suite with:

```bash
pytest
```

### API Overview

Current account endpoints:

- `GET /` – health check.
- `GET /ui` – basic HTML interface for managing accounts.
- `GET /accounts` – list all accounts.
- `POST /accounts` – create a new account.
- `PUT /accounts/{id}` – update an existing account.
- `DELETE /accounts/{id}` – remove an account.

## Notes
- Database files are stored under `./data/`. Ensure the directory exists before running the app.
- Refer to `CHANGELOG.md` for recent project updates.
