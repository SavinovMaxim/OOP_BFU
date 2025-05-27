from entities.user import User
from repositories.user import UserRepository
from services.auth import AuthService

if __name__ == "__main__":
    username = 'petya'
    password = 'asjkhfahkjfgakjh'
    email = 'example@example.com'

    repo = UserRepository("users.json", User)
    auth = AuthService("session.json", repo)

    # Добавление пользователя
    new_user = User(id=1, name="Петя", login=username, password=password, email=email)
    repo.add(new_user)

    user = repo.get_by_id(1)
    if user:
        user.name = "Петя Пупкин"
        repo.update(user)

    # Авторизация
    login_user = repo.get_by_login(username)
    if login_user and login_user.password == password:
        auth.sign_in(login_user)
        print(f"Авторизован: {auth.current_user.name}")

    # Смена пользователя
    auth.sign_out()
    print("Пользователь вышел.")

    # Повторный запуск покажет автологин
    if auth.is_authorized:
        print(f"Сессия восстановлена: {auth.current_user.name}")
    else:
        print("Нет активной сессии.")
