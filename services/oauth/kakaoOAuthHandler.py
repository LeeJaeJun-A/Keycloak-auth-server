from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from config.oauth import oauth_settings
import requests
import urllib.parse


class KakaoOAuthHandler:
    AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
    TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    USERINFO_URL = "https://kapi.kakao.com/v2/user/me"

    def get_redirect_url(self, request: Request) -> RedirectResponse:
        redirect_uri = str(request.url_for("oauth_callback", provider="kakao"))
        query_params = urllib.parse.urlencode({
            "client_id": oauth_settings.KAKAO_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
        })
        return RedirectResponse(url=f"{self.AUTH_URL}?{query_params}")

    async def exchange_code_and_get_token(self, code: str, request: Request) -> dict:
        redirect_uri = str(request.url_for("oauth_callback", provider="kakao"))

        token_response = requests.post(
            self.TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": oauth_settings.KAKAO_CLIENT_ID,
                "client_secret": oauth_settings.KAKAO_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=401, detail="KAKAO_OAUTH_TOKEN_EXCHANGE_FAILED")

        return token_response.json()

    async def get_user_info(self, token_data: dict) -> dict:
        access_token = token_data["access_token"]

        userinfo_response = requests.get(
            self.USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if userinfo_response.status_code != 200:
            raise HTTPException(status_code=401, detail="KAKAO_USERINFO_FETCH_FAILED")

        raw = userinfo_response.json()
        kakao_account = raw.get("kakao_account", {})
        profile = kakao_account.get("profile", {})

        email = kakao_account.get("email", "")
        full_name = profile.get("nickname", "")
        first_name = full_name
        last_name = ""

        return {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }
