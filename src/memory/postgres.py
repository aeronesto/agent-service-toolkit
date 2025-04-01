import logging

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.base import BaseStore
from langgraph.store.postgres import AsyncPostgresStore

from core.settings import settings

logger = logging.getLogger(__name__)


def validate_postgres_config() -> None:
    """
    Validate that all required PostgreSQL configuration is present.
    Raises ValueError if any required configuration is missing.
    """
    required_vars = [
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
    ]

    missing = [var for var in required_vars if not getattr(settings, var, None)]
    if missing:
        raise ValueError(
            f"Missing required PostgreSQL configuration: {', '.join(missing)}. "
            "These environment variables must be set to use PostgreSQL persistence."
        )


def get_postgres_connection_string() -> str:
    """Build and return the PostgreSQL connection string from settings."""
    return (
        f"postgresql://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD.get_secret_value()}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/"
        f"{settings.POSTGRES_DB}"
    )


def get_postgres_saver() -> BaseCheckpointSaver:
    """Initialize and return a PostgreSQL saver instance."""
    validate_postgres_config()
    return AsyncPostgresSaver.from_conn_string(get_postgres_connection_string())


def get_postgres_store():
    """
    Get a PostgreSQL store instance.
    
    Returns an AsyncPostgresStore instance that needs to be used with async context manager
    pattern according to the documentation:
    
    async with AsyncPostgresStore.from_conn_string(conn_string) as store:
        await store.setup()  # Run migrations
        # Use store...
    """
    validate_postgres_config()
    connection_string = get_postgres_connection_string()
    return AsyncPostgresStore.from_conn_string(connection_string)
