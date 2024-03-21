from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


def get_db_dependency(db_url: str):
    """
    Returns a coroutine function that provides a database session.

    Args:
        db_url (str): The URL of the database.

    Returns:
        coroutine: A coroutine function that, when called, returns a database session.

    Example:
        db = get_db_dependency("postgresql://user:password@localhost:5432/mydatabase")
        async with db() as session:
            # Use the session to interact with the database
            ...
    """
    async def get_db():
        engine = create_async_engine(db_url,echo=True)
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            yield session
    return get_db
