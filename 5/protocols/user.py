from typing import Protocol

from .data import DataRepositoryProtocol
from data.user import User


class UserRepositoryProtocol(DataRepositoryProtocol[User], Protocol):
    def get_by_login(self, login: str) -> User | None: ...
