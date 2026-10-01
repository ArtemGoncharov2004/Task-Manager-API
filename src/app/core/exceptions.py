class NotFoundError(Exception):
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail


class ConflictError(Exception):
    def __init__(self, detail: str = "Resource conflict"):
        self.detail = detail
