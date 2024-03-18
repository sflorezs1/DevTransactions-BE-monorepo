import firebase_admin
from firebase_admin import auth, credentials

# Initialize the Firebase app
cred = credentials.ApplicationDefault()
firebase_app = firebase_admin.initialize_app(cred)

def create_user(email, password):
    """ Creates a new Firebase user with email and password.

    Args:
        email: The email address of the user.
        password: The password of the user.

    Returns:
        firebase_admin.auth.UserRecord: The newly created user record.

    Raises:
        ValueError: If any of the arguments are invalid.
        firebase_admin.auth.AuthError: If there's an error creating the user with Firebase.
    """
    try:
        user = auth.create_user(
            email=email,
            password=password,
            app=firebase_app
        )
        return user
    except ValueError as e:
        raise ValueError(f"Invalid parameters for create_user: {e}")
    except auth.AuthError as e:
        raise auth.AuthError(f"Firebase Auth Error: {e}")

def get_user(uid):
    """ Retrieves a Firebase user by their UID.

    Args:
        uid: The user's unique identifier.

    Returns:
        firebase_admin.auth.UserRecord: The user record.

    Raises:
        firebase_admin.auth.AuthError: If the user is not found or there's an error with Firebase.
    """
    try:
        user = auth.get_user(uid, app=firebase_app)
        return user
    except auth.AuthError as e:
        raise auth.AuthError(f"Firebase Auth Error: {e}")