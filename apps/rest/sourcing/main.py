from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sourcing.security.router import router as security_router
from sourcing.source.aspsp.enable_banking import client as eb
from sourcing.source.router import router as source_router
from sourcing.user.router import router as user_router

origins = ["http://localhost:8080", "app://obsidian.md"]


@asynccontextmanager
async def lifespan(_: FastAPI):
    eb.startup()
    yield
    await eb.clean_up()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(security_router)
app.include_router(source_router)
