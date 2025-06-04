from fastapi import Request, Response, HTTPException
from jose import jwt, JWTError
from typing import Optional
import requests
from config.keycloak import settings


class TokenVerifier:
    def __init__(self):
        self.jwks = None

    def get_jwks(self):
        if self.jwks is None:
            self.jwks = self._fetch_jwks()
        return self.jwks

    def _fetch_jwks(self):
        response = requests.get(
            f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
        )
        response.raise_for_status()
        return response.json()

    def decode_token(self, token: str, audience="account") -> dict:
        try:
            return jwt.decode(
                token,
                self.get_jwks(),
                algorithms=["RS256"],
                audience=audience,
                options={"verify_aud": True},
            )
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"INVALID_TOKEN: {str(e)}")

    def try_refresh(self, refresh_token: str) -> dict:
        response = requests.post(
            f"http://{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token",
            data={
                "grant_type": "refresh_token",
                "client_id": settings.KEYCLOAK_CLIENT_ID,
                "refresh_token": refresh_token,
            },
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="REFRESH_FAILED")
        return response.json()

    def verify_preferred_username(payload: dict, expected_username: str) -> None:
        actual_username = payload.get("preferred_username")
        if actual_username != expected_username:
            raise HTTPException(status_code=401, detail="USERNAME_MISMATCH")


token_verifier = TokenVerifier()


async def authenticate_user(request: Request, response: Response) -> dict:
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="NO_ACCESS_TOKEN")

    refresh_token: Optional[str] = request.cookies.get("refresh_token")

    try:
        return token_verifier.decode_token(access_token)
    except HTTPException as e:
        print(f"[!] Access token decode 실패: {e.detail}")

        if not refresh_token:
            raise HTTPException(status_code=401, detail="NO_REFRESH_TOKEN")

        new_tokens = token_verifier.try_refresh(refresh_token)
        # TODO Need to change secure and samesite settings when you publish
        response.set_cookie(
            key="refresh_token",
            value=new_tokens["refresh_token"],
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        return token_verifier.decode_token(new_tokens["access_token"])


async def authenticate_and_verify_user(
    request: Request, response: Response, expected_username: str
) -> dict:
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="NO_ACCESS_TOKEN")

    refresh_token: Optional[str] = request.cookies.get("refresh_token")

    try:
        payload = token_verifier.decode_token(access_token)
    except HTTPException as e:
        print(f"[!] Access token decode 실패: {e.detail}")

        if not refresh_token:
            raise HTTPException(status_code=401, detail="NO_REFRESH_TOKEN")

        new_tokens = token_verifier.try_refresh(refresh_token)

        # TODO Need to change secure and samesite settings when you publish
        response.set_cookie(
            key="refresh_token",
            value=new_tokens["refresh_token"],
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        payload = token_verifier.decode_token(new_tokens["access_token"])

    TokenVerifier.verify_preferred_username(payload, expected_username)

    return payload
