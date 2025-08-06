# migrations/env.py

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. Ensure the project root is on sys.path so `import app` works
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2. Import your Settings and models after adjusting sys.path
from app.core.config import get_settings
from app.db.models import Base  # noqa: E402

# 3. Alembic Config object
config = context.config

# 4. Override the sqlalchemy.url in alembic.ini with your Settings value
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.POSTGRES_DSN)

# 5. Set up Python logging per alembic.ini (with safety check)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 6. Provide target_metadata for 'autogenerate'
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode: emit SQL without DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode: connect to DB and apply."""
    # Get the configuration section with safety check
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

# 7. Choose mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
