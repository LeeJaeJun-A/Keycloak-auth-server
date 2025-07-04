import requests
from getpass import getpass
from dotenv import set_key
import os
from dotenv import load_dotenv
import secrets

dotenv_path = os.path.join(os.path.dirname(__file__), ".env.keycloak")
load_dotenv(dotenv_path=dotenv_path, override=True)

DEFAULT_MASTER_USER = os.getenv("KEYCLOAK_ADMIN")
DEFAULT_MASTER_PASS = os.getenv("KEYCLOAK_ADMIN_PASSWORD")
DEFAULT_KEYCLOAK_URL = "http://localhost:8080"

def get_admin_token(master_username, master_password, keycloak_url):
    response = requests.post(
        f"{keycloak_url}/realms/master/protocol/openid-connect/token",
        data={
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": master_username,
            "password": master_password,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]

def create_realm(token, realm_name, keycloak_url):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(
        f"{keycloak_url}/admin/realms",
        headers=headers,
        json={"realm": realm_name, "enabled": True},
    )
    if response.status_code == 409:
        print(f"[i] Realm '{realm_name}' already exists. Skipping.")
    else:
        response.raise_for_status()
        print(f"[✓] Realm '{realm_name}' created.")

def create_roles(token, realm_name, role_names, keycloak_url):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    for role_name in role_names:
        response = requests.get(
            f"{keycloak_url}/admin/realms/{realm_name}/roles/{role_name}",
            headers=headers,
        )
        if response.status_code == 200:
            print(f"[i] Role '{role_name}' already exists. Skipping.")
            continue
        response = requests.post(
            f"{keycloak_url}/admin/realms/{realm_name}/roles",
            headers=headers,
            json={"name": role_name},
        )
        response.raise_for_status()
        print(f"[✓] Created role '{role_name}'.")

def create_user(token, realm_name, username, password, keycloak_url, email, first_name, last_name):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    user_data = {
        "username": username,
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "enabled": True,
        "credentials": [{"type": "password", "value": password, "temporary": False}],
        "requiredActions": [],
        "emailVerified": True,
    }
    response = requests.post(
        f"{keycloak_url}/admin/realms/{realm_name}/users",
        headers=headers,
        json=user_data,
    )
    if response.status_code == 409:
        print(f"[i] User '{username}' already exists. Skipping.")
    else:
        response.raise_for_status()
        print(f"[✓] User '{username}' created.")

def get_user_id(token, realm_name, username, keycloak_url):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{keycloak_url}/admin/realms/{realm_name}/users",
        headers=headers,
        params={"username": username},
    )
    response.raise_for_status()
    users = response.json()
    if users:
        return users[0]["id"]
    raise Exception(f"[!] User '{username}' not found.")

def get_client_id_by_client_id(token, realm_name, keycloak_url, client_id):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{keycloak_url}/admin/realms/{realm_name}/clients",
        headers=headers,
        params={"clientId": client_id},
    )
    resp.raise_for_status()
    clients = resp.json()
    if not clients:
        raise Exception(f"[!] Client '{client_id}' not found in realm '{realm_name}'")
    return clients[0]["id"]

def assign_realm_admin_role(token, realm_name, user_id, keycloak_url):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    client_id = get_client_id_by_client_id(token, realm_name, keycloak_url, "realm-management")
    role_resp = requests.get(
        f"{keycloak_url}/admin/realms/{realm_name}/clients/{client_id}/roles/realm-admin",
        headers=headers,
    )
    role_resp.raise_for_status()
    role = role_resp.json()
    assign_resp = requests.post(
        f"{keycloak_url}/admin/realms/{realm_name}/users/{user_id}/role-mappings/clients/{client_id}",
        headers=headers,
        json=[role],
    )
    assign_resp.raise_for_status()
    print("[✓] Assigned realm-admin role to user.")

def create_client(token, realm_name, client_id, keycloak_url):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    clients_resp = requests.get(
        f"{keycloak_url}/admin/realms/{realm_name}/clients",
        headers=headers,
        params={"clientId": client_id},
    )
    if clients_resp.json():
        print(f"[i] Client '{client_id}' already exists. Skipping.")
        return
    response = requests.post(
        f"{keycloak_url}/admin/realms/{realm_name}/clients",
        headers=headers,
        json={
            "clientId": client_id,
            "enabled": True,
            "protocol": "openid-connect",
            "publicClient": False,
            "redirectUris": ["*"],
            "directAccessGrantsEnabled": True,
            "serviceAccountsEnabled": True,
        },
    )
    response.raise_for_status()
    print(f"[✓] Client '{client_id}' created.")

def get_client_secret(token, realm_name, client_id, keycloak_url):
    headers = {"Authorization": f"Bearer {token}"}
    clients_resp = requests.get(
        f"{keycloak_url}/admin/realms/{realm_name}/clients",
        headers=headers,
        params={"clientId": client_id},
    )
    clients_resp.raise_for_status()
    clients = clients_resp.json()
    if not clients:
        raise Exception(f"[!] Client '{client_id}' not found.")
    client_uuid = clients[0]["id"]
    secret_resp = requests.get(
        f"{keycloak_url}/admin/realms/{realm_name}/clients/{client_uuid}/client-secret",
        headers=headers,
    )
    secret_resp.raise_for_status()
    return secret_resp.json()["value"]

def update_env_file(env_file, values):
    for key, value in values.items():
        set_key(env_file, key, value)
    print(f"[✓] Updated {env_file}")

def input_with_validation(prompt, default=None, required=False):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        elif default is not None:
            return default
        elif required:
            print("⚠️ 필수 입력 항목입니다. 다시 입력해주세요.")
        else:
            return ""

def getpass_with_validation(prompt):
    while True:
        value = getpass(prompt).strip()
        if value:
            return value
        print("⚠️ 필수 입력 항목입니다. 다시 입력해주세요.")

def generate_api_key(length: int = 32) -> str:
    return secrets.token_urlsafe(length)

def main():
    print("=== Keycloak Realm & Admin User Setup ===")
    keycloak_url = input(f"▶ Keycloak URL (default: {DEFAULT_KEYCLOAK_URL}): ").strip() or DEFAULT_KEYCLOAK_URL
    realm_name = input("▶ New Realm name: ").strip()
    admin_user = input("▶ Realm admin username: ").strip()
    admin_pass = getpass("▶ Admin password: ")
    admin_email = input("▶ Admin email (default: default@example.com ): ").strip() or "default@example.com"
    admin_first = input("▶ Admin first name (default: - ): ").strip() or "-"
    admin_last = input("▶ Admin last name (default: - ): ").strip() or "-"
    client_id = input("▶ Client ID (default: internal-api): ").strip() or "internal-api"

    token = get_admin_token(DEFAULT_MASTER_USER, DEFAULT_MASTER_PASS, keycloak_url)
    create_realm(token, realm_name, keycloak_url)
    create_roles(token, realm_name, ["admin", "user"], keycloak_url)
    create_user(token, realm_name, admin_user, admin_pass, keycloak_url, admin_email, admin_first, admin_last)
    user_id = get_user_id(token, realm_name, admin_user, keycloak_url)
    assign_realm_admin_role(token, realm_name, user_id, keycloak_url)
    create_client(token, realm_name, client_id, keycloak_url)
    secret = get_client_secret(token, realm_name, client_id, keycloak_url)

    api_key = generate_api_key()

    update_env_file(".env.keycloak-client", {
        "KEYCLOAK_URL": keycloak_url,
        "KEYCLOAK_REALM": realm_name,
        "KEYCLOAK_CLIENT_ID": client_id,
        "KEYCLOAK_CLIENT_SECRET": secret,
        "KEYCLOAK_ADMIN_USERNAME": admin_user,
        "KEYCLOAK_ADMIN_PASSWORD": admin_pass,
        "KEYCLOAK_API_KEY": api_key,
    })
    print("[✓] Setup complete.")

if __name__ == "__main__":
    main()