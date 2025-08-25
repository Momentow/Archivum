from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, select, col
from sqlalchemy import desc
import uuid
import shutil
import mimetypes

from .db import create_db_and_tables, get_session
from .models import Document

BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parents[0]
DATA_DIR = REPO_ROOT / "data"
FILES_DIR = DATA_DIR / "files"
TEXT_DIR  = DATA_DIR / "text"
FILES_DIR.mkdir(parents=True, exist_ok=True)
TEXT_DIR.mkdir(parents=True, exist_ok=True)

MAX_BYTES = 100 * 1024 * 1024  # 100 MB MVP cap

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

@app.get("/", response_class=HTMLResponse)
def index(request: Request, session: SessionDep):
    stmt = select(Document).order_by(col(Document.created_at).desc())
    docs = session.exec(stmt).all()
    return templates.TemplateResponse("index.html", {"request": request, "docs": docs})

@app.post("/upload")
async def upload(session: SessionDep, file: UploadFile = File(...)):
    # Light validation
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only .pdf files are supported for now.")
    mime, _ = mimetypes.guess_type(file.filename)
    if mime not in {"application/pdf", None}:
        raise HTTPException(400, "File is not a PDF.")

    # Save to disk with a safe name
    safe_name = f"{uuid.uuid4().hex}.pdf"
    dst = FILES_DIR / safe_name

    size = 0
    with dst.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_BYTES:
                out.close(); dst.unlink(missing_ok=True)
                raise HTTPException(413, "PDF too large (>100 MB).")
            out.write(chunk)

    # Create DB row (OCR still to come)
    doc = Document(
        original_name=file.filename,
        filename=safe_name,
        ocr_status="pending",
        text_path=None,
    )
    session.add(doc)
    session.commit()

    # Redirect to home so you see it in the list
    return RedirectResponse(url="/", status_code=303)
