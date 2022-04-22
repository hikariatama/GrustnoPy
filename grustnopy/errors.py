class EmailExistsError(Exception):
    """100: Email already exists"""


class LoginExistsError(Exception):
    """101: Login already exists"""


class UserNotFoundError(Exception):
    """102: User not found"""


class BadCredentialsError(Exception):
    """103: Wrong password"""


class UnknownError(Exception):
    """xxx: Unknown error"""
