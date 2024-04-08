from contextlib import asynccontextmanager

from fastapi import FastAPI

from sourcing.security.router import router as security_router
from sourcing.source.aspsp.enable_banking import client as eb
from sourcing.source.router import router as source_router
from sourcing.user.router import router as user_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    eb.startup()
    yield
    await eb.clean_up()


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(security_router)
app.include_router(source_router)
