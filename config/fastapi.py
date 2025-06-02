import os
from dotenv import load_dotenv

env_file = (
    ".env.docker" if os.getenv("IS_DOCKER", "false").lower() == "true" else ".env"
)

dotenv_path = os.path.join(os.path.dirname(__file__), env_file)
load_dotenv(dotenv_path=dotenv_path, override=True)

CORS_ALLOW_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOW_ORIGINS", "").split(",")
    if origin.strip()
]

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")