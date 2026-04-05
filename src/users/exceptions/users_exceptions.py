class TokenExpiredError(Exception):
    detail = "Token has expired"


class TokenIsNotCorrectError(Exception):
    detail = "Token is not correct"


class InvalidTokenTypeError(Exception):
    detail = "Invalid token type"


class InvalidTokenPayloadError(Exception):
    detail = "InvalidTokenPayload"


class PasswordIsNotCorrectError(Exception):
    detail = "Password is not correct"


class UserExistsError(Exception):
    detail = "User with this email yet created"


class UserNotFoundError(Exception):
    detail = "User not found"
