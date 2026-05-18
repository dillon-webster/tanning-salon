from hmac import compare_digest

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import get_admin_api_key

admin_api_key_header = APIKeyHeader(name="X-Admin-API-Key", auto_error=False)


def require_admin_api_key(
    provided_api_key: str | None = Security(admin_api_key_header),
) -> None:
    admin_api_key = get_admin_api_key()
    if not admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API key is not configured.",
        )
    if provided_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin API key is required.",
        )
    if not compare_digest(provided_api_key, admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin API key.",
        )
