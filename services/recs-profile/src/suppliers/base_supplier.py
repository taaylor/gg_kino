class BaseSupplier:
    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout
