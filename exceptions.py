class ClientUnavailableError(BaseException):
    pass


class ReceiveTimeoutError(BaseException):
    pass


class AckError(BaseException):
    pass


class LowBatteryError(BaseException):
    pass


class CoverOpenError(BaseException):
    pass


class NoPaperError(BaseException):
    pass


class WrongSmartSheetError(BaseException):
    pass
