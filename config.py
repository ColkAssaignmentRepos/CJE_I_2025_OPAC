from pathlib import Path

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DATABASE_FILE_PATH: Path = Path("/mount/gdrive/My Drive/cje1s2513929/database.sqlite3")
