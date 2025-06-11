from fastapi import APIRouter, HTTPException, status, Response, Request
from schemas.auth import LoginRequest
from services.user import KeycloakUserService

router = APIRouter(prefix="/api/v1/auth", tags=["Auth User"])


@router.post("/login", summary="Login with username and password")
def login(data: LoginRequest, response: Response):
    try:
        token = KeycloakUserService.login(data.username, data.password)
        # TODO Need to change secure and samesite settings when you publish
        response.set_cookie(
            key="access_token",
            value=token["access_token"],
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=token["expires_in"],
        )
        response.set_cookie(
            key="refresh_token",
            value=token["refresh_token"],
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=token["refresh_expires_in"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"INVALID_CREDENTIALS {str(e)}",
        )


@router.post("/logout", summary="Logout user by clearing tokens")
def logout(response: Response, request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        KeycloakUserService.logout(refresh_token)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"status": "success", "message": "Logged out successfully"}
