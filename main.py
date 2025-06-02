from fastapi import FastAPI
from api.auth import auth
from utils.keycloak_initializer import initialize_keycloak_roles

initialize_keycloak_roles()

app = FastAPI()
app.include_router(auth.router)
