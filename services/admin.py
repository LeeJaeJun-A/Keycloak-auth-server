from config.keycloak import keycloak_admin
from jose import jwt, JWTError
import requests
import traceback


class KeycloakAdminService:
    @staticmethod
    def create_user(
        username: str, email: str, password: str, first_name: str, last_name: str
    ):
        user = {
            "username": username,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": True,
            "emailVerified": True,
            "requiredActions": [],
            "credentials": [
                {
                    "type": "password",
                    "value": password,
                    "temporary": False,
                }
            ],
        }

        try:
            user_id = keycloak_admin.create_user(user)

            if user_id:
                try:
                    role = keycloak_admin.get_realm_role("user")
                    keycloak_admin.assign_realm_roles(user_id=user_id, roles=[role])
                except Exception as e:
                    print(f"[역할 할당 실패] {e}")
                    traceback.print_exc()

                return user_id

        except Exception as e:
            print(f"[사용자 생성 중 예외 발생] {e}")
            traceback.print_exc()
            return None

    @staticmethod
    def delete_user_by_username(username: str):
        users = keycloak_admin.get_users({"username": username})
        if not users:
            raise ValueError("User not found")

        user_id = users[0]["id"]
        keycloak_admin.delete_user(user_id)