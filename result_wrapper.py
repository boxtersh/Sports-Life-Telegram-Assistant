from dataclasses import dataclass
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    success: bool
    value: Optional[T] = None
    error: Optional[str] = None

    @classmethod
    def success(cls, value: T) -> 'Result[T]':
        return cls(success=True, value=value, error=None)

    @classmethod
    def failure(cls, error: str) -> 'Result[T]':
        return cls(success=False, value=None, error=error)