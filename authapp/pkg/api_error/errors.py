class ValidationError(Exception):
    """Raises when password is not valid."""


def api_errors(code: int, detail: str):
    return {"status_code": code, "detail": detail}, code
