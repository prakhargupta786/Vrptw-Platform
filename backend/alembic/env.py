from alembic import context
from sqlalchemy import engine_from_config, pool

import app.models  # noqa: F401  (registers all tables)
from app.core.config import settings
from app.db.base import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata

connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.",
                                 poolclass=pool.NullPool)
with connectable.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()
