import firebase_admin
from firebase_admin import auth, credentials
import requests
import aiohttp

from .config import FIREBASE_API_KEY

# Firebase project settings

async def create_user(email, password):
    """ Creates a new Firebase user with email and password.

    Args:
        email: The email address of the user.
        password: The password of the user.

    Returns:
        dict: The newly created user record.

    Raises:
        aiohttp.ClientResponseError: If there's an error creating the user with Firebase.
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    data = {"email": email, "password": password, "returnSecureToken": True}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            response.raise_for_status()  # Raises a ClientResponseError if the response was unsuccessful
            return await response.json()

async def get_user(uid):
    """ Retrieves a Firebase user by their UID.

    Args:
        uid: The user's unique identifier.

    Returns:
        dict: The user record.

    Raises:
        aiohttp.ClientResponseError: If the user is not found or there's an error with Firebase.
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}"
    data = {"localId": [uid]}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            response.raise_for_status()  # Raises a ClientResponseError if the response was unsuccessful
            return await response.json()
    
async def authenticate_user(email: str, password: str):
    """ Authenticates a user using their email and password.

    Args:
        email: The user's email.
        password: The user's password.

    Returns:
        str: The ID token if the authentication was successful, None otherwise.
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    data = {"email": email, "password": password, "returnSecureToken": True}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data.get('idToken')
    return None

async def verify_token(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={API_KEY}"
    data = {"idToken": id_token}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                return True
    return False