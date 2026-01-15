# morphkit/config.py
# SPDX-License-Identifier: CC-BY-4.0
# Copyright (c) 2026 Tony Jurg
"""Configuration management for Morphkit."""
from __future__ import annotations
__version__ = "1.0.1"

import os
from typing import Optional, Union

Number = Union[int, float]


class MorphkitConfig:
    """Global configuration for Morphkit HTTP interactions."""

    def __init__(self) -> None:
        self._timeout: Optional[Number] = 30
        self._retry_attempts: int = 3
        self._retry_delay: float = 1.0
        self._load_from_env()

    def _load_from_env(self) -> None:
        if timeout := os.getenv("MORPHKIT_TIMEOUT"):
            try:
                self._timeout = float(timeout)
            except ValueError:
                pass

        if retry_attempts := os.getenv("MORPHKIT_RETRY_ATTEMPTS"):
            try:
                self._retry_attempts = int(retry_attempts)
            except ValueError:
                pass

        if retry_delay := os.getenv("MORPHKIT_RETRY_DELAY"):
            try:
                self._retry_delay = float(retry_delay)
            except ValueError:
                pass

    @property
    def timeout(self) -> Optional[Number]:
        """Timeout in seconds for Morpheus HTTP requests."""
        return self._timeout

    @timeout.setter
    def timeout(self, value: Optional[Number]) -> None:
        if value is not None and value <= 0:
            raise ValueError("Timeout must be positive or None.")
        self._timeout = value

    @property
    def retry_attempts(self) -> int:
        """Number of retry attempts for failed requests."""
        return self._retry_attempts

    @retry_attempts.setter
    def retry_attempts(self, value: int) -> None:
        if value < 0:
            raise ValueError("Retry attempts must be non-negative.")
        self._retry_attempts = value

    @property
    def retry_delay(self) -> float:
        """Delay in seconds between retry attempts."""
        return self._retry_delay

    @retry_delay.setter
    def retry_delay(self, value: float) -> None:
        if value < 0:
            raise ValueError("Retry delay must be non-negative.")
        self._retry_delay = value


config = MorphkitConfig()
