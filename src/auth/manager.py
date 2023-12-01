from typing import Optional, Union

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, InvalidPasswordException, schemas, exceptions

from auth.config import SECRET_AUTH
from auth.models import User
from auth.schemas import UserCreate
from auth.utils import get_user_db


#  todo: проверки паролей и логинов, подумать насчет того чтобы можно было авторизоваться по логину, а не по e-mail.
async def validate_login(login: str) -> None:
    if len(login) < 6:
        raise InvalidPasswordException(reason="Login should be at least 6 characters")
    if len(login) > 40:
        raise InvalidPasswordException(reason="Login should be at more 40 characters")
    # if not login.isalpha():
    #     raise InvalidPasswordException(reason="Login should contain only letters")


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET_AUTH
    verification_token_secret = SECRET_AUTH

    async def create(self, user_create: schemas.UC, safe: bool = True, request: Optional[Request] = None) -> User:

        await validate_login(user_create.username)

        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def validate_password(self, password: str, user: Union[UserCreate, User]) -> None:
        if len(password) < 6:
            raise InvalidPasswordException(reason="Password should be at least 6 characters")
        if len(password) > 40:
            raise InvalidPasswordException(reason="Password should be at more 40 characters")
        # regex = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{6,40}$"
        # if not re.search(regex, password):
        #     raise InvalidPasswordException(
        #         reason="Password should contain at least one uppercase letter, one lowercase letter, and one digit")

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
