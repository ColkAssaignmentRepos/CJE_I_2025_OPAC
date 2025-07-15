import logging
from pathlib import Path

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DATABASE_FILE_PATH: Path = Path(
        "/mount/gdrive/My Drive/cje1s2513929/database.sqlite3"
    )

    @property
    def EFFECTIVE_ASYNC_DATABASE_URL(self) -> str:
        """
        Returns the effective async database URL.
        Falls back to a local file if the configured path is not available.
        """
        project_root = Path(__file__).resolve().parent

        # Check if the configured path is usable
        if (
            self.DATABASE_FILE_PATH.is_absolute()
            and self.DATABASE_FILE_PATH.parent.exists()
        ):
            db_path = self.DATABASE_FILE_PATH
        else:
            db_path = project_root / "database.sqlite3"
            logging.warning(f"Defaulting to local database at {db_path}")

        return f"sqlite+aiosqlite:///{db_path.resolve()}"
