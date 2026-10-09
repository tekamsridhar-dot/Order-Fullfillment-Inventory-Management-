class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str):
        self.status_code = status_code
        self.code = code
        self.message = message

        super().__init__(message)

class BadRequestException(AppException):
    def __init__(self, code: str, message: str):
        super().__init__(
            status_code=400,
            code=code,
            message=message)

class UnauthorizedException(AppException):
    def __init__(self, code: str, message: str):
        super().__init__(
            status_code=401,
            code=code,
            message=message)

class ForbiddenException(AppException):
    def __init__(self, code: str, message: str):
        super().__init__(
            status_code=403,
            code=code,
            message=message)

class NotFoundException(AppException):
    def __init__(self, code: str, message: str):
        super().__init__(
            status_code=404,
            code=code,
            message=message)

class ConflictException(AppException):
    def __init__(self, code: str, message: str):
        super().__init__(
            status_code=409,
            code=code,
            message=message)