from config.keycloak import keycloak_admin


class KeycloakAdminService:
    @staticmethod
    def create_user(username: str, email: str, password: str):
        user = {
            "username": username,
            "email": email,
            "enabled": True,
            "credentials": [
                {"type": "password", "value": password, "temporary": False}
            ],
        }

        user_id = keycloak_admin.create_user(user)

        if user_id:
            try:
                role = keycloak_admin.get_realm_role("user")
                keycloak_admin.assign_realm_roles(user_id=user_id, roles=[role])
            except Exception as e:
                print(f"[역할 할당 실패] {e}")
        else:
            print("[사용자 생성 실패 또는 이미 존재]")

        return user_id

    @staticmethod
    def delete_user(username: str) -> bool:
        try:
            users = keycloak_admin.get_users(query={"username": username})
            if not users:
                print(f"사용자 '{username}' 없음")
                return False

            user_id = users[0]["id"]
            keycloak_admin.delete_user(user_id)
            print(f"사용자 '{username}' 삭제 완료")
            return True

        except Exception as e:
            print(f"사용자 삭제 실패: {e}")
            return False
