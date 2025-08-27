from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
import uuid
import sqlalchemy as sa

def _utcnow() -> datetime:
    # Always store UTC
    return datetime.now(tz=timezone.utc)

class Document(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    original_name: str
    filename: str                                # stored filename on disk
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, index=True),
    )
    ocr_status: str = Field(default="pending")   # pending|processing|ready|failed
    text_path: str = ""                          # e.g., "/text/<id>.txt"
    detected_language: str = ""                  # e.g., "en"
