from fastapi import FastAPI

from sourcing.security.router import router as security_router
from sourcing.source.router import router as source_router
from sourcing.user.router import router as user_router

app = FastAPI()
app.include_router(user_router)
app.include_router(security_router)
app.include_router(source_router)
