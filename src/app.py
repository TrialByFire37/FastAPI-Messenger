from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import chat.router as chat_router
import room.router as room_router
import user.router as user_router
from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserUpdate, UserRead

app = FastAPI(title="PolyTex WebChat",
              version="0.0.1",
              root_path="/api/v1")

origins = [
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# auth
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# register
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# verify
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

# reset
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

# update user
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

app.include_router(
    user_router.router,
    prefix="/users",
    tags=["users"],
)

app.include_router(
    room_router.router,
    prefix="/rooms",
    tags=["rooms"],
)

app.include_router(
    chat_router.router,
)

current_user = fastapi_users.current_user()
