from fastapi import UploadFile, File, HTTPException
import mimetypes
import uuid
from pathlib import Path

from backend.app.vars import FILES_DIR, MAX_BYTES, ALLOWED_TYPES

def _detect_magic(head: bytes) -> tuple[str | None, str | None]:
    if head.startswith(b"%PDF-"):
        return ".pdf", "application/pdf"
    return None, None

def validate_file_upload(file: UploadFile) -> str:
    name = (file.filename or "").strip()
    if not name:
        raise HTTPException(400, "Missing filename.")

    # --- detect by magic ---
    head = file.file.read(8)
    file.file.seek(0)
    ext, mime = _detect_magic(head)
    if not ext or ext not in ALLOWED_TYPES:
        raise HTTPException(400, "Unsupported or unrecognized file type.")

    # --- cross-check MIME sources ---
    if ALLOWED_TYPES[ext] != mime:
        raise HTTPException(400, f"File type {ext} not allowed.")

    declared = (file.content_type or "").lower() or None
    if declared and declared != ALLOWED_TYPES[ext]:
        raise HTTPException(400, f"Content-Type '{declared}' doesn’t match {ALLOWED_TYPES[ext]}.")

    guessed, _ = mimetypes.guess_type(name)
    if guessed and guessed.lower() != ALLOWED_TYPES[ext]:
        raise HTTPException(400, f"Filename suggests '{guessed}', but detected {ALLOWED_TYPES[ext]}.")

    return ext

def make_safe_file_name(extension: str) -> str:
    return f"{uuid.uuid4().hex}{extension}"

async def save_upload_stream(file: UploadFile, dst: Path, *, max_bytes: int = MAX_BYTES) -> int:
    size = 0
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open("wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    # clean up partial file then report
                    out.close()
                    dst.unlink(missing_ok=True)
                out.write(chunk)
        return size
    except:
        # belt & suspenders cleanup on any error
        dst.unlink(missing_ok=True)
        raise


