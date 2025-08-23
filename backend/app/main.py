from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Annotated

from .db import create_db_and_tables, get_session
from .models import Document
from sqlmodel import Session, select, col

BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parents[1]
DATA_DIR = REPO_ROOT / "data"
FILES_DIR = DATA_DIR / "files"
TEXT_DIR  = DATA_DIR / "text"
FILES_DIR.mkdir(parents=True, exist_ok=True)
TEXT_DIR.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield


app = FastAPI(title="Archivum", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/files",  StaticFiles(directory=str(FILES_DIR)), name="files")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/healthz")
def healthz():
    return JSONResponse({"ok": True})

# Example read-only route using DI (kept for Step 4+)
@app.get("/_dev/docs")
def list_docs(session: SessionDep):
    stmt = select(Document).order_by(col(Document.created_at).desc())
    rows = session.exec(stmt).all()
    return [r.model_dump() for r in rows]


