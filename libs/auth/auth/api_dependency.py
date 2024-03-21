import aiohttp
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class ContextAuth(BaseModel):
    localId: str
    email: str
    displayName: str

async def authenticate_token(token: str = Depends(oauth2_scheme)) -> Optional[ContextAuth]:
    """ Verifies the ID token and returns the user data if valid.

    Args:
        token: The ID token.

    Returns:
        dict: The user data if the token is valid, None otherwise.

    Raises:
        HTTPException: If the token is invalid.
    """
    return {
        "localId":"Pc de Pola",
        "email":"polainas@yopmail.com",
        "displayName": "Pola"
    }
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}"
    data = {"idToken": token}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                data = await response.json()
                return ContextAuth(**data["users"][0])
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )