"""SQLModel models representing core entities for the application.

The models mirror the MVP specification and include helpful comments for
future maintainers. Relationships are defined using SQLModel's ORM features.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    status: str = "active"
    tags: Optional[str] = None  # Comma-separated tags for simplicity
    owner: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    contacts: List["Contact"] = Relationship(back_populates="account")
    tasks: List["Task"] = Relationship(back_populates="account")
    notes: List["Note"] = Relationship(back_populates="account")


class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None

    account: Account = Relationship(back_populates="contacts")
    tasks: List["Task"] = Relationship(back_populates="contact")
    notes: List["Note"] = Relationship(back_populates="contact")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    contact_id: Optional[int] = Field(default=None, foreign_key="contact.id")
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    status: str = Field(default="pending")
    priority: int = Field(default=0)
    attachments_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    account: Account = Relationship(back_populates="tasks")
    contact: Optional[Contact] = Relationship(back_populates="tasks")
    attachments: List["Attachment"] = Relationship(back_populates="task")
    notes: List["Note"] = Relationship(back_populates="task")


class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    contact_id: Optional[int] = Field(default=None, foreign_key="contact.id")
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    body_md: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    account: Account = Relationship(back_populates="notes")
    contact: Optional[Contact] = Relationship(back_populates="notes")
    task: Optional[Task] = Relationship(back_populates="notes")


class Attachment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    filename: str
    path: str
    size_bytes: int
    mime: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    soft_deleted: bool = Field(default=False)

    task: Task = Relationship(back_populates="attachments")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    password_hash: str
    theme_pref: Optional[str] = Field(default="system")
