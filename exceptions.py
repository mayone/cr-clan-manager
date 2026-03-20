from __future__ import annotations

from typing import Any


class APIError(Exception):
    """Raised when an API request returns a non-OK status code."""

    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self.payload = payload
        super().__init__(status_code, payload)

    def __str__(self) -> str:
        if isinstance(self.payload, dict):
            return f"APIError({self.status_code}, {self.payload})"
        return f"APIError({self.status_code}, {self.payload.text})"


class SheetError(Exception):
    """Raised when a Google Sheets operation fails."""
