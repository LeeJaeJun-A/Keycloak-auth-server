from fastapi import APIRouter, Request, Response
from services.oauth.oauth import OAuthService
from fastapi.responses import RedirectResponse
from config.keycloak import settings

router = APIRouter(prefix="/api/v1/oauth", tags=["OAuth"])

oauth_service = OAuthService()


@router.get("/login/{provider}", summary="Redirect to OAuth provider")
async def login_with_oauth(provider: str, request: Request):
    return oauth_service.get_redirect_to_authorization_url(provider, request)


@router.get(
    "/callback/{provider}", name="oauth_callback", summary="Handle OAuth callback"
)
async def oauth_callback(
    provider: str, code: str, request: Request, response: Response
):
    token_data = await oauth_service.handle_callback(provider, code, request)

    response.set_cookie(
        key="access_token",
        value=token_data["access_token"],
        httponly=True,
        secure=True,  # 운영환경에서는 반드시 True
        samesite="Lax",
        max_age=token_data.get("expires_in", 3600),
    )
    response.set_cookie(
        key="refresh_token",
        value=token_data["refresh_token"],
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=token_data.get("refresh_expires_in", 86400),
    )
    return {"status": "success"}


@router.post("/logout", summary="Logout for OAuth users")
def logout_oauth():
    logout_url = (
        f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}"
        f"/protocol/openid-connect/logout"
        f"?post_logout_redirect_uri=https://your-frontend-domain.com"
    )
    return RedirectResponse(url=logout_url)
