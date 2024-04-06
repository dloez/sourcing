from fastapi import FastAPI


from sourcing.user.router import router as user_router
from sourcing.security.router import router as security_router


app = FastAPI()
app.include_router(user_router)
app.include_router(security_router)
