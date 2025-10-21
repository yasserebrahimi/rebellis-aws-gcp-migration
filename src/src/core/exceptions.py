from typing import Any, Dict, Optional

class RebellisException(Exception):
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(RebellisException):
    def __init__(self, message: str = "Authentication failed"): super().__init__(message, 401)

class AuthorizationError(RebellisException):
    def __init__(self, message: str = "Insufficient permissions"): super().__init__(message, 403)

class ValidationError(RebellisException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None): super().__init__(message, 422, details)

class ResourceNotFoundError(RebellisException):
    def __init__(self, resource: str, id: Any): super().__init__(f"{resource} with id {id} not found", 404)

class ProcessingError(RebellisException): pass
class StorageError(RebellisException): pass
class MLModelError(RebellisException):
    def __init__(self, message: str, model_name: Optional[str] = None):
        details = {"model": model_name} if model_name else {}
        super().__init__(message, 500, details)
