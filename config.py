from pathlib import Path

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DATABASE_FILE_PATH: Path = Path(
        "/mount/gdrive/My Drive/cje1s2513929/database.sqlite3"
    )

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        # Use an in-memory SQLite database for default/testing if the path is not set
        if not self.DATABASE_FILE_PATH:
            return "sqlite+aiosqlite://"

        return f"sqlite+aiosqlite:///{self.DATABASE_FILE_PATH.resolve()}"
