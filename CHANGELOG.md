# Changelog

## Unreleased
- Documented virtual environment setup commands in README for clearer onboarding.
- Clarified activation, Windows usage, and deactivation steps for the virtual environment in README.
- Added cloning instructions to README for new developers.
- Updated cloning example to use the curlyphries GitHub account.
- Added logging to database initialization and session helpers for clearer troubleshooting.
- Expanded README with environment variables, testing instructions, and API overview.
- Updated model relationship annotations for compatibility with SQLAlchemy 2.0.
- Improved SQLite engine configuration to support in-memory testing environments.
- Adjusted account endpoints to return dictionaries for reliable Pydantic v2 serialization.
- Added new account routes for listing and retrieving account details.
- Improved error handling across account endpoints for clearer troubleshooting.
- Introduced pytest-based test suite for account routes and error scenarios.
- Scaffold FastAPI application with SQLModel-based data models and database utilities.
- Added basic account endpoints and health check.
- Created initial requirements file.
- Included placeholder `data/` directory for local SQLite storage.
- Wrapped account endpoints with SQLAlchemy error handling and logging for clearer troubleshooting.
- Added endpoints to update and delete accounts with consistent error handling.
- Added pytest suite for account CRUD endpoints and database error handling.
- Included pytest and httpx in requirements for testing.
