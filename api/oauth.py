from fastapi import APIRouter, Request, Depends, HTTPException
from services.oauth import KeycloakOAuthService
from schemas.oauth import OAuthCallbackRequest

router = APIRouter()
oauth_service = KeycloakOAuthService()


@router.post("/auth/oauth/callback")
async def oauth_callback(req: OAuthCallbackRequest):
    try:
        token = oauth_service.exchange_code_for_token(req.code, req.redirect_uri)
        user_info = oauth_service.get_user_info(token["access_token"])
        # DB 처리 또는 세션 처리 등 추가 로직 필요
        return {"access_token": token["access_token"], "user": user_info}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
