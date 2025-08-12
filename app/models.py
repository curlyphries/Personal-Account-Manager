"""SQLModel models representing core entities for the application.

The models mirror the MVP specification and include helpful comments for
future maintainers. Relationship fields are omitted for compatibility with
the lightweight test environment.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    status: str = "active"
    tags: Optional[str] = None  # Comma-separated tags for simplicity
    owner: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships to other entities (contacts, tasks, notes) are omitted to
    # keep the model compatible with newer SQLAlchemy versions used in tests.


class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None

    # Relationship fields are intentionally omitted for compatibility.


class Task(SQLModel, table=True):
    """Minimal task record used for basic reminders and follow‑ups.

    Only the fields required for the UI and tests are included. Additional
    metadata such as descriptions or priorities can be added later without
    impacting existing functionality.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: str = "pending"
    due_date: Optional[datetime] = None
    account_id: int = Field(foreign_key="account.id")

    # Relationship fields and auditing timestamps are intentionally omitted
    # to keep the model lightweight and focused for this iteration.


class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    contact_id: Optional[int] = Field(default=None, foreign_key="contact.id")
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    body_md: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship fields are intentionally omitted for compatibility.


class Attachment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    filename: str
    path: str
    size_bytes: int
    mime: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    soft_deleted: bool = Field(default=False)

    # Relationship field is intentionally omitted for compatibility.


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    password_hash: str
    theme_pref: Optional[str] = Field(default="system")
