from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager

# repo_root = .../archivum (two levels up from backend/app/)
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "archivum.db"
DB_URL = f"sqlite:///{DB_PATH.as_posix()}"

# check_same_thread=False allows using the connection in FastAPI threads
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@contextmanager
def get_session():
    with Session(engine) as session:
        yield session
