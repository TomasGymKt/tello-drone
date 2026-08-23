from __future__ import annotations

import importlib
import inspect
import pkgutil
from pathlib import Path

from utils.Logger import logger
from utils.color import C
from utils.errors import ScanningError

from .base import Scanner


SCANNERS: dict[str, Scanner] = {}


def _load_scanners() -> None:
    """Discover scanner modules and register their Scanner implementations."""
    package_dir = Path(__file__).resolve().parent

    for module_info in pkgutil.iter_modules([str(package_dir)]):
        module_name = module_info.name

        if module_name.startswith("_") or module_name in {"base", "wechat_models"}:
            continue

        module = importlib.import_module(f"{__name__}.{module_name}")
        scanner_class = getattr(module, "Scanner", None)

        if not inspect.isclass(scanner_class):
            continue

        if scanner_class is Scanner or not issubclass(scanner_class, Scanner):
            continue

        scanner = scanner_class()
        SCANNERS[scanner.method] = scanner
        globals()[scanner.method] = scanner


def get_scanner(method: str) -> Scanner:
    """Return a registered scanner backend.

    Args:
        method: Registered scanner method identifier.

    Returns:
        Scanner instance for the requested method.

    Raises:
        KeyError: If no scanner is registered for the method.
    """
    return SCANNERS[method]


def scan_with(method: str, frame):
    """Scan a frame with one backend while containing scanner failures.

    Args:
        method: Registered scanner method identifier.
        frame: Image to scan.

    Returns:
        Detected QR code, or None when scanning fails or finds nothing.
    """
    try:
        return get_scanner(method).scan(frame)
    except ScanningError:
        return None
    except Exception as e:
        logger.error(f"Unknown error while scanning with {method}:{C.RED}", e)
        print(C.RESET)
        return None


_load_scanners()

__all__ = ["Scanner", "SCANNERS", "get_scanner", "scan_with", *SCANNERS.keys()]
