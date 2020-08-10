class BaseCustomException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dict(self):
        return self.__dict__


class InternalError(BaseCustomException):
    def __init__(self, response: str = "ERROR", type: str = "Internal Error", message: str = ''):
        self.response = "ERROR"
        self.type = "Internal Error"
        self.message = message
