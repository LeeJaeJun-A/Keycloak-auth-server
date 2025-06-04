from fastapi import APIRouter, HTTPException, status, Response, Request
from schemas.auth import LoginRequest
from services.user import KeycloakUserService
from services.jwt_verification import authenticate_user, authenticate_and_verify_user

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


@router.get("/verify", summary="Verify access token only")
async def verify_token_only(
    request: Request,
    response: Response,
):
    payload = await authenticate_user(request, response)
    return {
        "status": "success",
        "preferred_username": payload.get("preferred_username"),
        "sub": payload.get("sub"),
    }


@router.get("/verify/user", summary="Verify access token and username")
async def verify_token_and_username(
    request: Request,
    response: Response,
    username: str,
):
    payload = await authenticate_and_verify_user(
        request, response, expected_username=username
    )
    return {
        "status": "success",
        "verified_username": payload.get("preferred_username"),
        "sub": payload.get("sub"),
    }
