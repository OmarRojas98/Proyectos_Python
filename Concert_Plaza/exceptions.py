from abc import ABC, abstractmethod

from fastapi import status


class BaseAPIException(ABC, Exception):
    """Base class for all API exceptions"""

    @property
    @abstractmethod
    def default_message(self) -> str:
        pass

    @property
    @abstractmethod
    def example_message(self) -> str:
        pass

    @property
    @abstractmethod
    def http_status_code(self) -> int:
        pass

    @classmethod
    def get_openapi_response(cls) -> dict:
        return {cls.http_status_code: {'description': cls.example_message}}

    def __init__(self, *args) -> None:
        if args:
            super().__init__(self.default_message.format(*args))
        else:
            super().__init__(self.default_message)


class NoLocationException(BaseAPIException):
    http_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_message = '{}'
    example_message = default_message


class NoSearchTermException(BaseAPIException):
    http_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_message = '{}'
    example_message = default_message


class FailedToGetURL(BaseAPIException):
    http_status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_message = '{}'
    example_message = default_message


class CompanyNameNotFoundError(Exception):
    """"""
