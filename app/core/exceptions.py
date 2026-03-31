from __future__ import annotations


class AppException(Exception):
    status_code: int = 500
    error: str = "internal_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundException(AppException):
    status_code = 404
    error = "not_found"


class BadRequestException(AppException):
    status_code = 400
    error = "bad_request"


class UnauthorizedException(AppException):
    status_code = 401
    error = "unauthorized"


class ConflictException(AppException):
    status_code = 409
    error = "conflict"
