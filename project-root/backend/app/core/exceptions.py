from fastapi import HTTPException, status

class UserNotRegisteredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="user_not_registered")

class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")