from datetime import datetime

from sqlmodel import Field, SQLModel


class Link(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True, max_length=10)
    url: str
    hits: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
