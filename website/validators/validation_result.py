from typing import Any, Dict, List, Optional


class ValidationResult:
    """Result object for validation operations"""

    def __init__(
        self,
        success: bool,
        message: str = None,
        code: str = None,
        errors: List[str] = None,
        data: Dict[str, Any] = None,
        obj: Any = None
    ):
        self.success = success
        self.message = message
        self.code = code
        self.errors = errors or []
        self.data = data or {}
        self.object = obj

    @classmethod
    def ok(cls, message: str = "Success", code: str = "success", obj: Any = None, data: Dict = None):
        """Create success result"""
        return cls(
            success=True,
            message=message,
            code=code,
            obj=obj,
            data=data
        )

    @classmethod
    def fail(cls, message: str, code: str = "error", errors: List[str] = None):
        """Create failure result"""
        return cls(
            success=False,
            message=message,
            code=code,
            errors=errors or [message]
        )

    def __bool__(self):
        """Allow if result: syntax"""
        return self.success