from enum import Enum


class Environment(str, Enum):
    TEST = "test"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

    def __str__(self):
        return self.value

class ErrorMessageCodes(str, Enum):
    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"