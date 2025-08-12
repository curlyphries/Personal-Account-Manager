# Personal Account Manager

A minimal FastAPI application for managing accounts, contacts, tasks, notes, and attachments. This project is intended for local use and serves as the foundation for a more feature-complete web app.

## Development Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`. A basic health check lives at the root endpoint.

## Notes
- Database files are stored under `./data/`. Ensure the directory exists before running the app.
- Refer to `CHANGELOG.md` for recent project updates.
