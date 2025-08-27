from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager

from backend.app.vars import REPO_ROOT, DATA_DIR, DB_PATH


engine = create_engine(f"sqlite:///{DB_PATH.as_posix()}",
                       connect_args={"check_same_thread": False})

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@contextmanager
def session_ctx():
    with Session(engine) as s:
        yield s

# FastAPI dependency (preferred in routes)
def get_db_session():
    with Session(engine) as s:
        yield s

