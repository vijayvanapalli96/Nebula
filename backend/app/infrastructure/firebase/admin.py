"""Firebase Admin SDK singleton — safe for multi-threaded ASGI workers."""
from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import firebase_admin
from firebase_admin import credentials, firestore

if TYPE_CHECKING:
    from google.cloud.firestore import Client

_lock = threading.Lock()
_app_initialized: bool = False
_db_initialized: bool = False
_db: "Client | None" = None


def _init_app() -> None:
    """Initialize the Firebase Admin app only (no Firestore client)."""
    global _app_initialized
    import os
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    cred = credentials.Certificate(cred_path) if cred_path else credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {"projectId": "disclosure-nlu"})
    _app_initialized = True


def ensure_initialized() -> None:
    """
    Ensure the Firebase Admin *app* is initialized (needed for auth.verify_id_token).
    Does NOT create a Firestore client — that is done lazily inside get_db().
    Call this before any firebase_admin.auth operation.
    """
    global _app_initialized
    if not _app_initialized:
        with _lock:
            if not _app_initialized:
                _init_app()


def get_db() -> "Client":
    """Return a Firestore client, initialising Firebase Admin once if needed."""
    global _app_initialized, _db_initialized, _db
    if not _app_initialized:
        with _lock:
            if not _app_initialized:
                _init_app()
    if not _db_initialized:
        with _lock:
            if not _db_initialized:
                _db = firestore.client()
                _db_initialized = True
    assert _db is not None
    return _db
