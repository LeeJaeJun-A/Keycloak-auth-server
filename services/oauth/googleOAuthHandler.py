from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from config.oauth import oauth_settings
import requests
import urllib.parse


class GoogleOAuthHandler:
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    def get_redirect_url(self, request: Request) -> RedirectResponse:
        redirect_uri = str(request.url_for("oauth_callback", provider="google"))
        query_params = urllib.parse.urlencode({
            "client_id": oauth_settings.GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        })
        return RedirectResponse(url=f"{self.AUTH_URL}?{query_params}")

    async def exchange_code_and_get_token(self, code: str, request: Request) -> dict:
        redirect_uri = str(request.url_for("oauth_callback", provider="google"))

        token_response = requests.post(
            self.TOKEN_URL,
            data={
                "code": code,
                "client_id": oauth_settings.GOOGLE_CLIENT_ID,
                "client_secret": oauth_settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=401, detail="GOOGLE_OAUTH_TOKEN_EXCHANGE_FAILED")

        return token_response.json()

    async def get_user_info(self, token_data: dict) -> dict:
        access_token = token_data["access_token"]

        userinfo_response = requests.get(
            self.USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if userinfo_response.status_code != 200:
            raise HTTPException(status_code=401, detail="GOOGLE_USERINFO_FETCH_FAILED")

        raw = userinfo_response.json()
        name_parts = raw.get("name", "").split(" ")
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        return {
            "email": raw.get("email"),
            "first_name": first_name,
            "last_name": last_name,
        }
