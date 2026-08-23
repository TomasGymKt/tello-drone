from __future__ import annotations

from abc import ABC, abstractmethod

from utils.models import QR_Code


class Scanner(ABC):
    """Abstract interface implemented by QR-code scanner backends."""
    method: str

    @abstractmethod
    def scan(self, frame) -> QR_Code | None:
        """Scan an image for one QR code.

        Args:
            frame: Image to inspect.

        Returns:
            Detected QR code, or None when no code is found.
        """
        raise NotImplementedError
