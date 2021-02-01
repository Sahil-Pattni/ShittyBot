# Exception class for Binance API
class ApiError(Exception):
    def __init__(message):
        self.message = message
        super().__init__(self.message)