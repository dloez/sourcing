from fastapi import FastAPI


from sourcing.user.router import router as user_router


app = FastAPI()
app.include_router(user_router)


# async def authenticate_user(email: EmailStr, password: str) -> User | None:
#     user = await users.find_one({"email": email})
#     user = User(**user)

#     if not user:
#         return None
#     if not cryptContext.verify(password, user.password):
#         return None
#     return user


# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = await get_user_by_email(email=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user


# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# async def get_user_by_email(email: EmailStr) -> User | None:
#     user = await users.find_one({"email": email})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return User(**user)


# @app.get("/users/me", response_model=ReturnUser, response_model_by_alias=False)
# async def get_user(current_user: Annotated[User, Depends(get_current_active_user)]):
#     return current_user

# @app.post("/token")
# async def login_for_access_token(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
# ) -> Token:
#     user = await authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     access_token = create_access_token(
#         data={"sub": user.email}, expires_delta=access_token_expires
#     )
#     return Token(access_token=access_token, token_type="bearer")
