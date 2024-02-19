from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.concurrency import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from src.database import get_db_session, sessionmanager
from src.schemas.user_schema import UserCreate
import src.user.user_service as crud

import src.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()

app = FastAPI(lifespan=lifespan)


@app.post("/users/")
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db_session)]):
    return await crud.create_user(db=db, user=user)

@app.get("/users/{user_id}")
async def read_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db_session)]):
    user = await crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
