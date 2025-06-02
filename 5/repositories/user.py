from data.user import User
from protocols.user import UserRepositoryProtocol
from repositories.base import DataRepository


class UserRepository(DataRepository[User], UserRepositoryProtocol):
    def get_by_login(self, login: str) -> User | None:
        for user in self._datas:
            if user.login == login:
                return user
        return None
