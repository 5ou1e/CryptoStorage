import secrets
from typing import Optional, Union

from fastapi_users.password import (
    PasswordHelperProtocol,
)
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


class ArgonPasswordHasher(PasswordHelperProtocol):
    """Для совместимости с префиксами в Django"""

    algorithm = "argon2"

    def __init__(
        self,
        password_hash: Optional[PasswordHash] = None,
    ) -> None:
        if password_hash is None:
            self.password_hash = PasswordHash((Argon2Hasher(),))
        else:
            self.password_hash = password_hash  # pragma: no cover

    def verify_and_update(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> tuple[bool, Union[str, None]]:
        hashed_password = "$" + hashed_password.split("$", 1)[1]
        return self.password_hash.verify_and_update(plain_password, hashed_password)

    def hash(self, password: str) -> str:
        return self.algorithm + self.password_hash.hash(password)

    def generate(self) -> str:
        return self.algorithm + secrets.token_urlsafe()


password_hasher_argon = ArgonPasswordHasher()
