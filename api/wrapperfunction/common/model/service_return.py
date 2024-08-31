from enum import Enum
from typing import Any, Dict

class StatusCode(Enum):
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    # Add other status codes as needed

class ServiceReturn:
    def __init__(self, status: StatusCode, message: str, data: Any = None):
        self.status = status
        self.message = message
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status_code": self.status.value,  # Numeric value of the enum
            "status": self.status.name,  # Name of the enum (e.g., "SUCCESS")
            "message": self.message,
            "data": self.data
        }
