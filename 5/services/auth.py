import json
import logging
from pathlib import Path

from data.user import User
from protocols.auth import AuthServiceProtocol
from protocols.user import UserRepositoryProtocol

class AuthService(AuthServiceProtocol):
    def __init__(self, session_file: str = "session.json", repo: UserRepositoryProtocol = None):
        self.session_file = Path(session_file)
        self._current_user: User | None = None
        self.repo = repo
        self._load_session()

    def _load_session(self):
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if self.repo:
                        user = self.repo.get_by_id(data["id"])
                        self._current_user = user
                    else:
                        logging.error("UserRepository not provided. Cannot load session.")
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON in '{self.session_file}'")
            except KeyError:
                logging.error(f"'id' key not found in '{self.session_file}'")
            except Exception as e:
                logging.error(f"Error reading '{self.session_file}': {e}")


    def _save_session(self):
        if self._current_user:
            try:
                with open(self.session_file, 'w', encoding='utf-8') as f:
                    json.dump({"id": self._current_user.id}, f)
            except Exception as e:
                logging.error(f'Error saving session file: {e}, current user id: {self._current_user.id}')


    def sign_in(self, user: User) -> None:
        self._current_user = user
        self._save_session()

    def sign_out(self) -> None:
        self._current_user = None
        if self.session_file.exists():
            self.session_file.unlink()

    @property
    def is_authorized(self) -> bool:
        return self._current_user is not None

    @property
    def current_user(self) -> User | None:
        return self._current_user

