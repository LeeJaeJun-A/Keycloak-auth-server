from fastapi import FastAPI
from api import auth
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from config.fastapi import CORS_ALLOW_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)