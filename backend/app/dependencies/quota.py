"""
Storage quota enforcement dependencies.

Checks are cached for CACHE_TTL seconds to avoid hitting the filesystem
on every request. On Linux the file-size calls are essentially free, but
caching prevents even the small overhead from stacking up under load.
"""

import os
import time
from pathlib import Path

from fastapi import HTTPException, status

from app.database import BASE_DIR, DATABASE_DIR

# ─── Limits ──────────────────────────────────────────────────────────────────

DB_LIMIT_BYTES    = 20 * 1024 ** 3   # 20 GB
IMAGE_LIMIT_BYTES = 80 * 1024 ** 3   # 80 GB

# ─── Image storage root ───────────────────────────────────────────────────────

# Covers both data/images and data/uploads so nothing slips through.
_IMAGE_DIRS: list[Path] = [
    BASE_DIR / "data" / "images",
    BASE_DIR / "data" / "uploads",
]

# ─── Cache (per-process, refreshed every 60 s) ───────────────────────────────

CACHE_TTL = 60  # seconds

_db_cache: dict = {"size": 0, "ts": 0.0}
_img_cache: dict = {"size": 0, "ts": 0.0}


# ─── Size helpers ─────────────────────────────────────────────────────────────

def _db_size_bytes() -> int:
    """Return the current size of the SQLite database file in bytes."""
    db_file = DATABASE_DIR / "garage.db"
    try:
        return os.path.getsize(db_file)
    except FileNotFoundError:
        return 0


def _image_size_bytes() -> int:
    """Return the total bytes occupied by all files in the image directories."""
    total = 0
    for image_dir in _IMAGE_DIRS:
        if not image_dir.exists():
            continue
        for dirpath, _, filenames in os.walk(image_dir):
            for fname in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, fname))
                except OSError:
                    pass
    return total


# ─── Cached accessors ─────────────────────────────────────────────────────────

def get_db_size() -> int:
    now = time.monotonic()
    if now - _db_cache["ts"] > CACHE_TTL:
        _db_cache["size"] = _db_size_bytes()
        _db_cache["ts"] = now
    return _db_cache["size"]


def get_image_size() -> int:
    now = time.monotonic()
    if now - _img_cache["ts"] > CACHE_TTL:
        _img_cache["size"] = _image_size_bytes()
        _img_cache["ts"] = now
    return _img_cache["size"]


# ─── FastAPI dependencies ─────────────────────────────────────────────────────

def require_db_quota() -> None:
    """
    Dependency for any route that writes to the database.

    Raises HTTP 507 Insufficient Storage when the database file
    reaches or exceeds DB_LIMIT_BYTES (20 GB).
    """
    if get_db_size() >= DB_LIMIT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            detail=(
                "The database has reached its storage limit. "
                "No new records can be added. Please contact the administrator."
            ),
        )


def require_image_quota() -> None:
    """
    Dependency for any route that stores image files.

    Raises HTTP 507 Insufficient Storage when the total size of stored
    images reaches or exceeds IMAGE_LIMIT_BYTES (80 GB).
    """
    if get_image_size() >= IMAGE_LIMIT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            detail=(
                "The image storage has reached its capacity limit. "
                "No new images can be uploaded. Please contact the administrator."
            ),
        )
