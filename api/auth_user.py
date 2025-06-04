from fastapi import APIRouter, HTTPException, status
from schemas.auth import LoginRequest
from services.user import KeycloakUserService

router = APIRouter(prefix="/api/v1/auth", tags=["Auth User"])


@router.post("/login", summary="Login with username and password")
def login(data: LoginRequest):
    try:
        token = KeycloakUserService.login(data.username, data.password)
        return {
            "access_token": token["access_token"],
            "refresh_token": token["refresh_token"],
            "expires_in": token["expires_in"],
            "refresh_expires_in": token["refresh_expires_in"],
            "token_type": token["token_type"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"INVALID_CREDENTIALS {str(e)}",
        )
