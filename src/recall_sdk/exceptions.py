class RecallError(Exception):
    """Base exception for all Recall SDK errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ContractError(RecallError):
    """Raised when a contract operation fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ObjectNotFoundError(RecallError):
    """Raised when an object cannot be found."""

    def __init__(self, bucket: str, key: str):
        self.message = f"Object not found: {bucket}/{key}"
        super().__init__(self.message)


class UnexpectedError(RecallError):
    """Raised for unexpected errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
