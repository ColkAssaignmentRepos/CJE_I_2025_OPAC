import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

# Add project root to sys.path
# This allows alembic to find the 'src' and 'config' modules
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from config import Config
from src.db._model import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from the config file
# Use a default value if the config is not set
app_config = Config()
db_path = (
    app_config.DATABASE_FILE_PATH
    if app_config.DATABASE_FILE_PATH.is_absolute()
    else project_root / app_config.DATABASE_FILE_PATH
)
# Fallback to a local sqlite file if the configured path's parent does not exist
if not db_path.parent.exists():
    db_path = project_root / "database.sqlite3"
    print(f"Warning: Defaulting to local database at {db_path}")

config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
