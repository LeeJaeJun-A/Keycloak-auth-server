from fastapi import APIRouter, HTTPException, Response, Request, Depends
from services.jwt_verification import token_verifier
from services.keycloak_api_key_verification import verify_api_key
from typing import Optional
from config.keycloak import settings
import requests

router = APIRouter(prefix="/api/v1/token", tags=["Token"])


@router.get("/verify", summary="Verify access token only")
async def verify_token_only(
    request: Request,
    response: Response,
):
    payload = await token_verifier.get_valid_token_payload(request, response)
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
    payload = await token_verifier.get_valid_token_payload(request, response)
    token_verifier.verify_preferred_username(payload, username)
    return {
        "status": "success",
        "verified_username": payload.get("preferred_username"),
        "sub": payload.get("sub"),
    }


@router.post("/refresh", summary="Issue new tokens with refresh token")
async def refresh_tokens(request: Request):
    refresh_token: Optional[str] = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="NO_REFRESH_TOKEN")

    try:
        new_tokens = token_verifier.try_refresh(refresh_token)
        return {
            "status": "success",
            "access_token": new_tokens["access_token"],
            "refresh_token": new_tokens["refresh_token"],
        }
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"UNKNOWN_ERROR: {str(e)}")


@router.get(
    "/public-key",
    summary="Provide JWT public keys",
    dependencies=[Depends(verify_api_key)],
)
def get_public_jwks():
    try:
        response = requests.get(
            f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        raise HTTPException(
            status_code=502, detail="Failed to fetch JWKs from Keycloak"
        )
