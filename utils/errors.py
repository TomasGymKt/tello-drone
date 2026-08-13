class ConnectionError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

class ScanningError(Exception):
    def __init__(self, scanning_method: str, base_error: Exception, msg: str = ""):
        self.scanning_method = scanning_method
        self.base_error = base_error
        self.msg = msg