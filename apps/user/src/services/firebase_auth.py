import firebase_admin
from firebase_admin import auth


class FirebaseAuthService:
    def __init__(self, firebase_app):
        """ Initializes the FirebaseAuthService class.

        Args:
            firebase_app: A FirebaseApp object representing your initialized Firebase app. 
        """
        self.firebase_app = firebase_app

    def create_user(self, email, password):
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
                app=self.firebase_app
            )
            return user
        except ValueError as e:
            raise ValueError(f"Invalid parameters for create_user: {e}")
        except auth.AuthError as e:
            raise auth.AuthError(f"Firebase Auth Error: {e}")

    def get_user(self, uid):
        """ Retrieves a Firebase user by their UID.

        Args:
            uid: The user's unique identifier.

        Returns:
            firebase_admin.auth.UserRecord: The user record.

        Raises:
            firebase_admin.auth.AuthError: If the user is not found or there's an error with Firebase.
        """
        try:
            user = auth.get_user(uid, app=self.firebase_app)
            return user
        except auth.AuthError as e:
            raise auth.AuthError(f"Firebase Auth Error: {e}")
        
    def decode_token(self, id_token):
        """ Decodes a Firebase ID token.

        Args:
            id_token: The Firebase ID token to decode.

        Returns:
            dict: The decoded token.

        Raises:
            firebase_admin.auth.InvalidIdTokenError: If the ID token is invalid.
            firebase_admin.auth.ExpiredIdTokenError: If the ID token is expired.
            firebase_admin.auth.RevokedIdTokenError: If the ID token has been revoked.
            firebase_admin.auth.UserDisabledError: If the user corresponding to the ID token has been disabled.
        """
        return auth.verify_id_token(id_token)

    # ... (Add more methods for updating user data, deleting users, etc.)
        
# **How to Use:**
# 1. Install the firebase_admin library: `pip install firebase-admin`
# 2. Initialize your Firebase App (refer to Firebase documentation)
# 3. Create an instance of this class

