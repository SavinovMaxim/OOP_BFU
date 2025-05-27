from functools import lru_cache


class Settings:
    ENCODING = 'utf-8'
    DEFAULT_MEMENTO_FILE = 'keyboard.json'


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
