import fastapi
from fastapi import (FastAPI, Depends, UploadFile, File, HTTPException, Request)
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, select, col

from backend.app.vars import BASE_DIR, FILES_DIR, TEXT_DIR, MAX_BYTES
from backend.app.db import create_db_and_tables, get_db_session
from backend.app.models import Document
from backend.app.utils import (validate_file_upload, make_safe_file_name, save_upload_stream)


# defines projects initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [Startup]
    # -> create db + tables -> init logger -> [normal work]
    create_db_and_tables()
    yield

app = FastAPI(title="Archivum", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/files",  StaticFiles(directory=str(FILES_DIR)), name="files")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
SessionDep = Annotated[Session, Depends(get_db_session)]


@app.get("/healthz")
def healthz():
    return JSONResponse({"ok": True})

@app.get("/", response_class=HTMLResponse)
def index(request: Request, session: SessionDep):
    stmt = select(Document).order_by(col(Document.created_at).desc())
    docs = session.exec(stmt).all()
    return templates.TemplateResponse("index.html", {"request": request, "docs": docs})

@app.post("/upload")
async def upload(session: SessionDep, file: UploadFile = File(...)):

    file_extension = validate_file_upload(file)

    # Save to disk with a safe name
    safe_name = make_safe_file_name(file_extension)
    dst = FILES_DIR / safe_name

    file_size = await save_upload_stream(file, dst)

    if file_size > MAX_BYTES:
        raise HTTPException(413, f"Document is too large (>{MAX_BYTES // (1024 * 1024)} MB).")

    # Create DB row (OCR still to come)
    doc = Document(
        original_name=file.filename or "",
        filename=safe_name,
    )
    session.add(doc)
    session.commit()
    
    # Redirect to home so you see it in the list
    return RedirectResponse(url="/", status_code=303)

# Example read-only route using DI
@app.get("/_dev/docs")
def list_docs(session: SessionDep):
    stmt = select(Document).order_by(col(Document.created_at).desc())
    rows = session.exec(stmt).all()
    return [r.model_dump() for r in rows]
