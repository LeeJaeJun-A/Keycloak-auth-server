from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from config.oauth import oauth_settings
import requests
import urllib.parse


class NaverOAuthHandler:
    AUTH_URL = "https://nid.naver.com/oauth2.0/authorize"
    TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
    USERINFO_URL = "https://openapi.naver.com/v1/nid/me"

    def get_redirect_url(self, request: Request) -> RedirectResponse:
        redirect_uri = str(request.url_for("oauth_callback", provider="naver"))
        query_params = urllib.parse.urlencode(
            {
                "client_id": oauth_settings.NAVER_CLIENT_ID,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "state": "naver_state",  # CSRF 방지용. 필요 시 동적으로 생성 가능
            }
        )
        return RedirectResponse(url=f"{self.AUTH_URL}?{query_params}")

    async def exchange_code_and_get_token(self, code: str, request: Request) -> dict:
        redirect_uri = str(request.url_for("oauth_callback", provider="naver"))

        token_response = requests.post(
            self.TOKEN_URL,
            params={
                "grant_type": "authorization_code",
                "client_id": oauth_settings.NAVER_CLIENT_ID,
                "client_secret": oauth_settings.NAVER_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "code": code,
                "state": "naver_state",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=401, detail="NAVER_OAUTH_TOKEN_EXCHANGE_FAILED"
            )

        return token_response.json()

    async def get_user_info(self, token_data: dict) -> dict:
        access_token = token_data["access_token"]

        userinfo_response = requests.get(
            self.USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if userinfo_response.status_code != 200:
            raise HTTPException(status_code=401, detail="NAVER_USERINFO_FETCH_FAILED")

        raw = userinfo_response.json()
        response = raw.get("response", {})

        email = response.get("email")
        name = response.get("name", "")
        first_name = name.split(" ")[0] if name else ""
        last_name = " ".join(name.split(" ")[1:]) if len(name.split(" ")) > 1 else ""

        return {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }
