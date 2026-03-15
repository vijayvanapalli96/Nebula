"""POST /api/users/create — idempotent user-document upsert in Firestore."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator

from app.infrastructure.firebase.admin import get_db
from app.presentation.api.dependencies import require_auth

router = APIRouter(prefix="/api/users", tags=["users"])


# ── Pydantic models ──────────────────────────────────────────────────────────


class CreateUserRequest(BaseModel):
    uid: str
    email: str
    displayName: Optional[str] = None
    photoURL: Optional[str] = None
    provider: Literal["password", "google"]

    @field_validator("uid", "email")
    @classmethod
    def _not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()


class UserOut(BaseModel):
    uid: str
    email: str
    displayName: Optional[str] = None
    photoURL: Optional[str] = None
    provider: str
    createdAt: str
    updatedAt: str
    lastLoginAt: str
    role: str
    status: str


class CreateUserResponse(BaseModel):
    success: bool
    user: dict[str, Any]


# ── Helpers ──────────────────────────────────────────────────────────────────


def _serialize(data: dict[str, Any]) -> dict[str, Any]:
    """Coerce Firestore Timestamp / datetime to ISO-8601 string for JSON."""
    result: dict[str, Any] = {}
    for k, v in data.items():
        if isinstance(v, datetime):
            result[k] = v.isoformat()
        elif hasattr(v, "isoformat"):
            result[k] = v.isoformat()
        else:
            result[k] = v
    return result


# ── Route ─────────────────────────────────────────────────────────────────────


@router.post(
    "/create",
    response_model=CreateUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update a Firestore user document",
)
async def create_or_update_user(
    body: CreateUserRequest,
    token_uid: str = Depends(require_auth),
) -> CreateUserResponse:
    """
    Idempotent upsert for the ``users/{uid}`` Firestore document.

    * **New user** — creates the document with ``createdAt``, ``updatedAt``,
      ``lastLoginAt``, ``role = "user"``, and ``status = "active"``.
    * **Returning user** — only updates ``lastLoginAt`` and ``updatedAt``.

    The caller's Firebase ID-token UID **must match** the ``uid`` field in the
    request body, preventing one user from mutating another's document.
    """
    # Security: token UID must match requested UID
    if token_uid != body.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token UID does not match request UID.",
        )

    try:
        db = get_db()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Firestore unavailable: {exc}",
        ) from exc

    user_ref = db.collection("users").document(body.uid)

    try:
        doc = user_ref.get()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Firestore read failed: {exc}",
        ) from exc

    now = datetime.now(timezone.utc)

    # ── Existing user — update login timestamps ──────────────────────────────
    if doc.exists:
        try:
            user_ref.update({"lastLoginAt": now, "updatedAt": now})
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Firestore update failed: {exc}",
            ) from exc

        user_data: dict[str, Any] = doc.to_dict() or {}
        user_data["lastLoginAt"] = now
        user_data["updatedAt"] = now
        return CreateUserResponse(success=True, user=_serialize(user_data))

    # ── New user — create document ───────────────────────────────────────────
    user_data = {
        "uid":         body.uid,
        "email":       body.email,
        "displayName": body.displayName,
        "photoURL":    body.photoURL,
        "provider":    body.provider,
        "createdAt":   now,
        "updatedAt":   now,
        "lastLoginAt": now,
        "role":        "user",
        "status":      "active",
    }
    try:
        user_ref.set(user_data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Firestore write failed: {exc}",
        ) from exc

    return CreateUserResponse(success=True, user=_serialize(user_data))
