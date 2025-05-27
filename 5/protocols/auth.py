from typing import Protocol

from entities.user import User


class AuthServiceProtocol(Protocol):
    def sign_in(self, user: User) -> None: ...

    def sign_out(self) -> None: ...

    @property
    def is_authorized(self) -> bool: ...

    @property
    def current_user(self) -> User | None: ...
