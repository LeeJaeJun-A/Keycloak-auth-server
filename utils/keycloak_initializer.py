from config.keycloak import keycloak_admin

REQUIRED_REALM_ROLES = ["user", "root_user"]


def initialize_keycloak_roles():
    existing_roles = [role["name"] for role in keycloak_admin.get_realm_roles()]

    for role_name in REQUIRED_REALM_ROLES:
        if role_name not in existing_roles:
            keycloak_admin.create_realm_role({"name": role_name})
            print(f"Created missing realm role: {role_name}")
