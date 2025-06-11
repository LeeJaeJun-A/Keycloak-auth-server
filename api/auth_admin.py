from fastapi import APIRouter, HTTPException, status, Request, Response
from schemas.auth import EmailRequest, CodeVerifyRequest, RegisterRequest
from services.email_verification import email_service
from services.admin import KeycloakAdminService
from services.jwt_verification import token_verifier

router = APIRouter(prefix="/api/v1/auth", tags=["Auth Admin"])


@router.post("/send-code", summary="Send verification code to email")
def send_code(data: EmailRequest):
    ttl = email_service.send_verification_code(data.email)
    return {
        "message": f"A verification code has been sent to {data.email}.",
        "ttl_seconds": ttl,
    }


@router.post("/verify-code", summary="Verify email code")
def verify_code(data: CodeVerifyRequest):
    success, remaining = email_service.verify_code(data.email, data.code)

    if success:
        email_service.mark_verified(data.email)
        return {"message": "Email verification successful"}

    if remaining is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SESSION_INVALID_OR_EXPIRED",
                "message": "The verification session is invalid or has expired.",
            },
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "code": "INVALID_CODE",
            "message": "Invalid code entered.",
            "attempts_left": remaining,
        },
    )


@router.post("/register", summary="Register user (after email verification)")
def register(data: RegisterRequest):
    if not email_service.is_verified(data.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="EMAIL_NOT_VERIFIED",
        )

    user_id = KeycloakAdminService.create_user(
        username=data.username,
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name
    )
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="USER_ALREADY_EXISTS_OR_CREATION_FAILED",
        )

    return {"message": "Registration successful", "user_id": user_id}


@router.delete("/{username}", summary="Delete user by username")
async def delete_user(username: str, request: Request, response: Response):
    # 1. 인증된 사용자 정보 가져오기
    payload = await token_verifier.get_valid_token_payload(request, response)
    current_username = payload.get("preferred_username")

    # 2. 본인 확인
    if current_username != username:
        raise HTTPException(status_code=403, detail="Can only delete your own account")

    try:
        # 3. Keycloak에서 사용자 삭제
        KeycloakAdminService.delete_user_by_username(username)

        # 4. 로그아웃 처리 (쿠키 삭제)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return {"status": "success", "message": f"User '{username}' deleted and logged out."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"USER_DELETE_FAILED: {str(e)}")