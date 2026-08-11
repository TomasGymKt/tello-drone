from __future__ import annotations

from abc import ABC, abstractmethod

from utils.models import QR_Code


class Scanner(ABC):
    method: str

    @abstractmethod
    def scan(self, frame) -> QR_Code | None:
        raise NotImplementedError
