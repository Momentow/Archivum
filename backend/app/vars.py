from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parents[0]
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = REPO_ROOT / "data"
FILES_DIR = DATA_DIR / "files"
FILES_DIR.mkdir(parents=True, exist_ok=True)
TEXT_DIR  = DATA_DIR / "text"
TEXT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "archivum.db"

MAX_BYTES = 100 * 1024 * 1024  # 100 MB max file size
ALLOWED_TYPES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
    ".webp": "image/webp",
}
ALLOWED_EXT = set(ALLOWED_TYPES.keys())
ALLOWED_MIME = set(ALLOWED_TYPES.values())

def show_paths():
    print("\tProject paths:")
    print("BASE_DIR:\t", BASE_DIR)
    print("REPO_ROOT:\t", REPO_ROOT)
    print("DATA_DIR:\t", DATA_DIR)
    print("FILES_DIR:\t", FILES_DIR)
    print("TEXT_DIR:\t", TEXT_DIR)
    print("DB_PATH:\t", DB_PATH)

if __name__ == "__main__":
    show_paths()
