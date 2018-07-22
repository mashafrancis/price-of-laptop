import uuid

import src.models.users.errors as UserErrors

from src.common.database import Database
from src.common.utils import Utils


class User:
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<User {}".format(self.email)

    @staticmethod
    def is_login_valid(email, password):
        """
        This method verifies that an email/password (sent from the site form) is valid
        Checks that the email exists and password is correct
        :param email: The user's email
        :param password: The sha512 hashed password
        :return: True if valid, False otherwise
        """
        user_data = Database.find_one("users", {"email": email})  # Password in sha512 -> pbkdf2_sha512
        if user_data is None:
            # Tell the user that the email does not exist
            raise UserErrors.UserNotExistsError("Your user does not exist.")
        if not Utils.check_hashed_password(password, user_data['password']):
            raise UserErrors.IncorrectPasswordError("Your password is wrong.")

        return True

    @staticmethod
    def register_user(email, password):
        """
        This method register a user using email and password.
        The password already comes hashed as sha-512
        :param email: User's email (might be invalid)
        :param password: sha512-hashed password
        :return: True if registered successfully, or False otherwise
        """
        user_data = Database.find_one("users", {"email": email})

        if user_data is not None:
            raise UserErrors.UserAlreadyRegisteredError("The email already exists.")
        if not Utils.email_is_valid(email):
            raise UserErrors.InvalidEmailError("The email does not have the right format.")

        User(email, Utils.hash_password(password)).save_to_db()

        return True

    def save_to_db(self):
        Database.insert("users", self.json())

    def json(self):
        return {
            "_id": self._id,
            "email": self.email,
            "password": self.password
        }
