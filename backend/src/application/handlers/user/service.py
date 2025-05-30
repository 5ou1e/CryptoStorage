import uuid
from typing import Any, Optional, TypeVar, Union

import jwt
import pytz
from fastapi import Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from fastapi_users.password import PasswordHelper, PasswordHelperProtocol

from src.application.common.exceptions import (
    InvalidAccessTokenException,
    InvalidResetPasswordTokenException,
    InvalidUserIDException,
    UserAlreadyExistsException,
    UserAlreadyVerifiedException,
    UserDoesNotExistsException,
    UserInactiveException,
)
from src.application.common.interfaces.repositories.user import UserRepositoryInterface
from src.application.common.interfaces.uow import UnitOfWorkInterface
from src.application.handlers.user.dto import UserCreateDTO, UserUpdateDTO
from src.domain.entities.base_entity import BaseEntity
from src.domain.entities.user import User

RESET_PASSWORD_TOKEN_AUDIENCE = "fastapi-users:reset"
VERIFY_USER_TOKEN_AUDIENCE = "fastapi-users:verify"

ID = TypeVar("ID")


class UUIDIDMixin:
    def parse_id(self, value: Any) -> uuid.UUID:  # noqa
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except ValueError as e:
            raise InvalidUserIDException() from e


class IntegerIDMixin:
    def parse_id(self, value: Any) -> int:  # noqa
        if isinstance(value, float):
            raise InvalidUserIDException()
        try:
            return int(value)
        except ValueError as e:
            raise InvalidUserIDException() from e


class UserService(UUIDIDMixin):
    """
    User management logic.

    :attribute reset_password_token_secret: Secret to encode reset password token.
    :attribute reset_password_token_lifetime_seconds: Lifetime of reset password token.
    :attribute reset_password_token_audience: JWT audience of reset password token.
    :attribute verification_token_secret: Secret to encode verification token.
    :attribute verification_token_lifetime_seconds: Lifetime of verification token.
    :attribute verification_token_audience: JWT audience of verification token.

    :param user_db: Database adapter instance.
    """

    reset_password_token_secret: SecretType
    reset_password_token_lifetime_seconds: int = 3600
    reset_password_token_audience: str = RESET_PASSWORD_TOKEN_AUDIENCE

    verification_token_secret: SecretType
    verification_token_lifetime_seconds: int = 3600
    verification_token_audience: str = VERIFY_USER_TOKEN_AUDIENCE

    def __init__(
        self,
        uow: UnitOfWorkInterface,
        user_repository: UserRepositoryInterface,
        password_helper: PasswordHelperProtocol,
    ):
        self._uow = uow
        self._user_repository = user_repository
        self.password_helper = password_helper  # pragma: no cover

    async def get(self, id_: ID) -> User:
        """
        Get a user by id.
        """
        user = await self._user_repository.get_by_id(id_)
        if user is None:
            raise UserDoesNotExistsException()
        return user

    async def get_by_email(self, user_email: str) -> User:
        """
        Get a user by e-mail.
        """
        user = await self._user_repository.get_by_email(user_email)
        if user is None:
            raise UserDoesNotExistsException()
        return user

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> User:
        """
        Get a user by OAuth account.
        """
        user = await self._user_repository.get_by_oauth_account(oauth, account_id)

        if user is None:
            raise UserDoesNotExistsException()

        return user

    async def create(
        self,
        user_create: UserCreateDTO,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        """
        Create a user in database.
        Triggers the on_after_register handler on success.
        :return: A new user.
        """
        async with self._uow as uow:
            await self.validate_password(user_create.password, user_create)

            existing_user = await self._user_repository.get_by_email(user_create.email)
            if existing_user is not None:
                raise UserAlreadyExistsException(email=user_create.email)
            # user_dict = (
            #     user_create.create_update_dict()
            #     if safe
            #     else user_create.create_update_dict_superuser()
            # )
            user = User.create(
                username=user_create.username,
                email=user_create.email,
                hashed_password=self.password_helper.hash(user_create.password),
            )
            created_user = await self._user_repository.create(user)
            await self.on_after_register(created_user, request)

            return created_user

    async def oauth_callback(
        self,
        oauth_name: str,
        access_token: str,
        account_id: str,
        account_email: str,
        expires_at: Optional[int] = None,
        refresh_token: Optional[str] = None,
        request: Optional[Request] = None,
        *,
        associate_by_email: bool = False,
        is_verified_by_default: bool = False,
    ) -> BaseEntity:
        """
        Handle the callback after a successful OAuth authentication.

        If the user already exists with this OAuth account, the token is updated.

        If a user with the same e-mail already exists and `associate_by_email` is True,
        the OAuth account is associated to this user.
        Otherwise, the `UserNotExists` exception is raised.

        If the user does not exist, it is created and the on_after_register handler
        is triggered.

        :param oauth_name: Name of the OAuth client.
        :param access_token: Valid access token for the service provider.
        :param account_id: models.ID of the user on the service provider.
        :param account_email: E-mail of the user on the service provider.
        :param expires_at: Optional timestamp at which the access token expires.
        :param refresh_token: Optional refresh token to get a
        fresh access token from the service provider.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None
        :param associate_by_email: If True, any existing user with the same
        e-mail address will be associated to this user. Defaults to False.
        :param is_verified_by_default: If True, the `is_verified` flag will be
        set to `True` on newly created user. Make sure the OAuth Provider you're
        using does verify the email address before enabling this flag.
        Defaults to False.
        :return: A user.
        """
        oauth_account_dict = {
            "oauth_name": oauth_name,
            "access_token": access_token,
            "account_id": account_id,
            "account_email": account_email,
            "expires_at": expires_at,
            "refresh_token": refresh_token,
        }

        try:
            user = await self.get_by_oauth_account(oauth_name, account_id)
        except UserDoesNotExistsException:
            try:
                # Associate account
                user = await self.get_by_email(account_email)
                if not associate_by_email:
                    raise UserAlreadyExistsException(email=account_email)
                user = await self._user_repository.add_oauth_account(user, oauth_account_dict)
            except UserDoesNotExistsException:
                # Create account
                password = self.password_helper.generate()
                user_dict = {
                    "email": account_email,
                    "hashed_password": self.password_helper.hash(password),
                    "is_verified": is_verified_by_default,
                }
                user = await self._user_repository.create(user_dict)
                user = await self._user_repository.add_oauth_account(user, oauth_account_dict)
                await self.on_after_register(user, request)
        else:
            # Update oauth
            for existing_oauth_account in user.oauth_accounts:
                if existing_oauth_account.account_id == account_id and existing_oauth_account.oauth_name == oauth_name:
                    user = await self._user_repository.update_oauth_account(
                        user,
                        existing_oauth_account,
                        oauth_account_dict,
                    )

        return user

    async def oauth_associate_callback(
        self,
        user: models.UOAP,
        oauth_name: str,
        access_token: str,
        account_id: str,
        account_email: str,
        expires_at: Optional[int] = None,
        refresh_token: Optional[str] = None,
        request: Optional[Request] = None,
    ) -> models.UOAP:
        """
        Handle the callback after a successful OAuth association.

        We add this new OAuth account to the given user.

        :param oauth_name: Name of the OAuth client.
        :param access_token: Valid access token for the service provider.
        :param account_id: models.ID of the user on the service provider.
        :param account_email: E-mail of the user on the service provider.
        :param expires_at: Optional timestamp at which the access token expires.
        :param refresh_token: Optional refresh token to get a
        fresh access token from the service provider.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None
        :return: A user.
        """
        oauth_account_dict = {
            "oauth_name": oauth_name,
            "access_token": access_token,
            "account_id": account_id,
            "account_email": account_email,
            "expires_at": expires_at,
            "refresh_token": refresh_token,
        }

        user = await self._user_repository.add_oauth_account(user, oauth_account_dict)

        await self.on_after_update(user, {}, request)

        return user

    async def request_verify(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        """
        Start a verification request.

        Triggers the on_after_request_verify handler on success.

        :param user: The user to verify.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserInactive: The user is inactive.
        :raises UserAlreadyVerified: The user is already verified.
        """
        if not user.is_active:
            raise UserInactiveException()
        if user.is_verified:
            raise UserAlreadyVerifiedException()

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )
        await self.on_after_request_verify(user, token, request)

    async def verify(
        self,
        token: str,
        request: Optional[Request] = None,
    ) -> User:
        """
        Validate a verification request.

        Changes the is_verified flag of the user to True.

        Triggers the on_after_verify handler on success.

        :param token: The verification token generated by request_verify.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises InvalidVerifyToken: The token is invalid or expired.
        :raises UserAlreadyVerified: The user is already verified.
        :return: The verified user.
        """
        try:
            data = decode_jwt(
                token,
                self.verification_token_secret,
                [self.verification_token_audience],
            )
        except jwt.PyJWTError:
            raise InvalidAccessTokenException(token)

        try:
            user_id = data["sub"]
            email = data["email"]
        except KeyError:
            raise InvalidAccessTokenException(token)

        try:
            user = await self.get_by_email(email)
        except UserDoesNotExistsException:
            raise InvalidAccessTokenException(token)

        try:
            parsed_id = self.parse_id(user_id)
        except InvalidUserIDException:
            raise InvalidAccessTokenException(token)

        if parsed_id != user.id:
            raise InvalidAccessTokenException(token)

        if user.is_verified:
            raise UserAlreadyVerifiedException()

        verified_user = await self._update(user, {"is_verified": True})

        await self.on_after_verify(verified_user, request)

        return verified_user

    async def forgot_password(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        """
        Start a forgot password request.

        Triggers the on_after_forgot_password handler on success.

        :param user: The user that forgot its password.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserInactive: The user is inactive.
        """
        if not user.is_active:
            raise UserInactiveException()

        token_data = {
            "sub": str(user.id),
            "password_fgpt": self.password_helper.hash(user.hashed_password),
            "aud": self.reset_password_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.reset_password_token_secret,
            self.reset_password_token_lifetime_seconds,
        )
        await self.on_after_forgot_password(user, token, request)

    async def reset_password(
        self,
        token: str,
        password: str,
        request: Optional[Request] = None,
    ) -> User:
        """
        Reset the password of a user.

        Triggers the on_after_reset_password handler on success.

        :param token: The token generated by forgot_password.
        :param password: The new password to set.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises InvalidResetPasswordToken: The token is invalid or expired.
        :raises UserInactive: The user is inactive.
        :raises InvalidPasswordException: The password is invalid.
        :return: The user with updated password.
        """
        try:
            data = decode_jwt(
                token,
                self.reset_password_token_secret,
                [self.reset_password_token_audience],
            )
        except jwt.PyJWTError:
            raise InvalidResetPasswordTokenException(token)

        try:
            user_id = data["sub"]
            password_fingerprint = data["password_fgpt"]
        except KeyError:
            raise InvalidResetPasswordTokenException(token)

        try:
            parsed_id = self.parse_id(user_id)
        except InvalidUserIDException:
            raise InvalidResetPasswordTokenException(token)

        user = await self.get(parsed_id)

        valid_password_fingerprint, _ = self.password_helper.verify_and_update(
            user.hashed_password,
            password_fingerprint,
        )
        if not valid_password_fingerprint:
            raise InvalidResetPasswordTokenException(token)

        if not user.is_active:
            raise UserInactiveException()

        updated_user = await self._update(user, {"password": password})

        await self.on_after_reset_password(user, request)

        return updated_user

    async def update(
        self,
        user_update: UserUpdateDTO,
        user: User,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        """
        Update a user.

        Triggers the on_after_update handler on success

        :param user_update: The UserUpdateDTO model containing
        the changes to apply to the user.
        :param user: The current user to update.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the update, defaults to False
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :return: The updated user.
        """
        if safe:
            updated_user_data = user_update.create_update_dict()
        else:
            updated_user_data = user_update.create_update_dict_superuser()
        updated_user = await self._update(user, updated_user_data)
        await self.on_after_update(
            updated_user,
            updated_user_data,
            request,
        )
        return updated_user

    async def delete(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        """
        Delete a user.

        :param user: The user to delete.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        await self.on_before_delete(user, request)
        await self._user_repository.delete(user)
        await self.on_after_delete(user, request)

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreateDTO, User],
    ) -> None:
        """
        Validate a password.

        *You should overload this method to add your own validation logic.*

        :param password: The password to validate.
        :param user: The user associated to this password.
        :raises InvalidPasswordException: The password is invalid.
        :return: None if the password is valid.
        """
        return  # pragma: no cover

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        """
        Perform logic after successful user registration.

        *You should overload this method to add your own logic.*

        :param user: The registered user
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_update(
        self,
        user: User,
        update_dict: dict[str, Any],
        request: Optional[Request] = None,
    ) -> None:
        """
        Perform logic after successful user update.

        *You should overload this method to add your own logic.*

        :param user: The updated user
        :param update_dict: Dictionary with the updated user fields.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ) -> None:
        """
        Perform logic after successful verification request.

        *You should overload this method to add your own logic.*

        :param user: The user to verify.
        :param token: The verification token.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_verify(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        """
        Perform logic after successful user verification.

        *You should overload this method to add your own logic.*

        :param user: The verified user.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ) -> None:
        """
        Perform logic after successful forgot password request.

        *You should overload this method to add your own logic.*

        :param user: The user that forgot its password.
        :param token: The forgot password token.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_reset_password(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        """
        Perform logic after successful password reset.

        *You should overload this method to add your own logic.*

        :param user: The user that reset its password.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ) -> None:
        """
        Perform logic after user login.

        *You should overload this method to add your own logic.*

        :param user: The user that is logging in
        :param request: Optional FastAPI request
        :param response: Optional response built by the transport.
        Defaults to None
        """
        return  # pragma: no cover

    async def on_before_delete(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        """
        Perform logic before user delete.

        *You should overload this method to add your own logic.*

        :param user: The user to be deleted
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_delete(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        """
        Perform logic before user delete.

        *You should overload this method to add your own logic.*

        :param user: The user to be deleted
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def authenticate(
        self,
        credentials: OAuth2PasswordRequestForm,
    ) -> Optional[User]:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.

        :param credentials: The user credentials.
        """
        try:
            user = await self.get_by_email(credentials.username)
        except UserDoesNotExistsException:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password,
            user.hashed_password,
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            user.hashed_password = updated_password_hash
            async with self._uow:
                await self._user_repository.update(
                    user,
                    # {"hashed_password": updated_password_hash},
                )

        return user

    async def _update(
        self,
        user: User,
        update_dict: dict[str, Any],
    ) -> User:
        for field, value in update_dict.items():
            if field == "email" and value != user.email:
                try:
                    await self.get_by_email(value)
                    raise UserAlreadyExistsException(email=value)
                except UserDoesNotExistsException:
                    setattr(user, "email", value)
                    setattr(user, "is_verified", False)
            elif field == "password" and value is not None:
                await self.validate_password(value, user)
                setattr(user, "hashed_password", self.password_helper.hash(value))
            else:
                setattr(user, field, value)
        return await self._user_repository.update(user)
