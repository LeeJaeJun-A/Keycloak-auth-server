import random
import string
import os
from redis import Redis
from datetime import timedelta


class EmailVerificationService:
    CODE_TTL = 300
    ATTEMPT_LIMIT = 5
    VERIFIED_TTL = 600

    KEY_CODE = "email_code:{}"
    KEY_ATTEMPTS = "email_attempts:{}"
    KEY_VERIFIED = "verified_email:{}"

    def __init__(self):
        self.r = Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=6379,
            decode_responses=True,
        )

    def _key_code(self, email: str) -> str:
        return self.KEY_CODE.format(email)

    def _key_attempts(self, email: str) -> str:
        return self.KEY_ATTEMPTS.format(email)

    def _key_verified(self, email: str) -> str:
        return self.KEY_VERIFIED.format(email)

    def _generate_code(self, length=6) -> str:
        return "".join(random.choices(string.digits, k=length))

    def send_verification_code(self, email: str) -> int:
        code = self._generate_code()
        self.r.setex(self._key_code(email), timedelta(seconds=self.CODE_TTL), code)
        self.r.setex(
            self._key_attempts(email),
            timedelta(seconds=self.CODE_TTL),
            self.ATTEMPT_LIMIT,
        )

        # TODO 실제 인증 이메일 보내도록
        print(f"[DEBUG] Sent to {email}: code = {code}")
        return self.CODE_TTL

    def verify_code(self, email: str, code: str) -> tuple[bool, int | None]:
        attempts_key = self._key_attempts(email)
        stored_code = self.r.get(self._key_code(email))
        attempts = self.r.get(attempts_key)

        if attempts is None:
            return False, None

        attempts_left = int(attempts)
        if attempts_left <= 0:
            return False, 0

        if code != stored_code:
            self.r.decr(attempts_key)
            return False, attempts_left - 1

        self.r.delete(self._key_code(email))
        self.r.delete(attempts_key)
        return True, None

    def mark_verified(self, email: str) -> None:
        self.r.set(self._key_verified(email), "true", ex=self.VERIFIED_TTL)

    def is_verified(self, email: str) -> bool:
        return self.r.get(self._key_verified(email)) == "true"


email_service = EmailVerificationService()
