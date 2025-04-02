import secrets
from typing import Optional, Union

from fastapi_users.password import PasswordHelperProtocol
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


class ArgonPasswordHasher(PasswordHelperProtocol):
    """Для совместимости с префиксами в Django"""

    algorithm = "argon2"

    def __init__(
        self,
    ) -> None:
        self.password_hash = PasswordHash((Argon2Hasher(),))  # pragma: no cover

    def verify_and_update(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> tuple[bool, Union[str, None]]:
        hashed_password = "$" + hashed_password.split("$", 1)[1]
        verified, updated_password_hash = self.password_hash.verify_and_update(plain_password, hashed_password)
        updated_password_hash = (
            self.algorithm + updated_password_hash if updated_password_hash else updated_password_hash
        )
        return verified, updated_password_hash

    def hash(self, password: str) -> str:
        return self.algorithm + self.password_hash.hash(password)

    def generate(self) -> str:
        return self.algorithm + secrets.token_urlsafe()
