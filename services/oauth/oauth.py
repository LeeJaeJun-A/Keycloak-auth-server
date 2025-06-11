from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from services.oauth.googleOAuthHandler import GoogleOAuthHandler
from services.oauth.kakaoOAuthHandler import KakaoOAuthHandler
from services.oauth.naverOAuthHandler import NaverOAuthHandler
from services.admin import KeycloakAdminService


class OAuthService:
    handlers = {
        "google": GoogleOAuthHandler(),
        "kakao": KakaoOAuthHandler(),
        "naver": NaverOAuthHandler(),
    }

    def get_redirect_to_authorization_url(
        self, provider: str, request: Request
    ) -> RedirectResponse:
        handler = self.handlers.get(provider)
        if not handler:
            raise HTTPException(status_code=400, detail="Unsupported provider")
        return handler.get_redirect_url(request)

    async def handle_callback(self, provider: str, code: str, request: Request):
        handler = self.handlers.get(provider)
        if not handler:
            raise HTTPException(status_code=400, detail="Unsupported provider")

        token_data = await handler.exchange_code_and_get_token(code, request)
        user_info = await handler.get_user_info(token_data)

        KeycloakAdminService.sync_user_from_oauth(
            email=user_info["email"],
            first_name=user_info.get("first_name", ""),
            last_name=user_info.get("last_name", ""),
            login_type=provider,
        )

        return {
            "token": token_data,
            "userinfo": user_info,
        }
