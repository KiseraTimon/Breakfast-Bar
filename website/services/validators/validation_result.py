from typing import Any, Dict, List, Optional

class ValidationResult:
    """Class of expected validation outcomes"""
    # Attributes
    success: bool                           # Success State
    object: Optional[Any] = None            # Payload
    data: Optional[Dict[str, Any]] = None   # Processed Data
    errors: Optional[List[str]] = None      # Errors
    code: Optional[str] = None              # Output Category

    # Successful Validation Events
    @classmethod
    def ok(cls, obj: Any = None, data: Dict[str, Any] = None, code: str = "ok"):
        inst = cls()
        inst.success = True
        inst.object = obj
        inst.data = data or {}
        inst.errors = []
        inst.code = code
        return inst

    # Failed Validation Events
    @classmethod
    def fail(cls, msg: str, code: str = "error", errors: Optional[List[str]] = None):
        inst = cls()
        inst.success = False
        inst.object = None
        inst.data = {}
        inst.errors = (errors or [msg])
        inst.code = code
        return inst