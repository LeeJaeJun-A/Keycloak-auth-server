from fastapi import APIRouter, HTTPException, status
from schemas.auth import EmailRequest, CodeVerifyRequest, RegisterRequest
from services.email_verification import email_service
from services.admin import KeycloakAdminService

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


# TODO 자기 자신만 삭제할 수 있도록 JWT 토큰 검증(회원탈퇴)
@router.delete("/{username}", summary="Delete user by username")
def delete_user(username: str):
    pass



