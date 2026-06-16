from enum import Enum
from datetime import datetime


class LogLevel(Enum):
  TEST = -1
  DEBUG = 0
  INFO = 1
  WARN = 2
  ERROR = 3
  FATAL = 4


LEVEL_COLORS = {
  LogLevel.TEST: "\033[92m",   # světle zelená
  LogLevel.DEBUG: "\033[95m",  # fialová
  LogLevel.INFO: "\033[96m",   # světle modrá
  LogLevel.WARN: "\033[93m",   # žlutá
  LogLevel.ERROR: "\033[91m",  # červená
  LogLevel.FATAL: "\033[31m",  # tmavě červená
}

RESET = "\033[0m"


class Logger:
  def __init__(self, min_level: LogLevel = LogLevel.DEBUG):
    self.min_level = min_level

  def _should_log(self, level: LogLevel) -> bool:
    return level.value >= self.min_level.value

  def _format_message(
    self,
    level: LogLevel,
    message: str | list[str]
  ) -> list[str]:
    timestamp = datetime.now().strftime("%H:%M:%S")

    if isinstance(message, str):
      message = [message]

    color = LEVEL_COLORS[level]
    level_text = f"{color}{level.name}{RESET}"

    return [
      f"[{timestamp}] [{level_text}]: {message[0]}",
      *message[1:]
    ]

  def _write(
    self,
    level: LogLevel,
    message: str | list[str],
    meta: object | None = None
  ) -> None:
    if not self._should_log(level):
      return

    formatted = self._format_message(level, message)

    if level == LogLevel.FATAL:
      line = "=" * 100
      print(f"\n{line}")
      print(formatted[0])

      for extra in formatted[1:]:
        print(extra)

      if meta:
        print(meta)

      print(line)
      return

    print(formatted[0])

    for extra in formatted[1:]:
      print(extra)

    if meta:
      print(meta)

  def test(self, message: str | list[str], meta: object = None):
    self._write(LogLevel.TEST, message, meta)

  def debug(self, message: str | list[str], meta: object = None):
    self._write(LogLevel.DEBUG, message, meta)

  def info(self, message: str | list[str], meta: object = None):
    self._write(LogLevel.INFO, message, meta)

  def success(self, message: str | list[str], meta: object = None):
    self._write(LogLevel.INFO, f"\033[92m{message}\033[0m", meta)

  def warn(self, message: str | list[str], meta: object = None):
    self._write(LogLevel.WARN, message, meta)

  def error(self, message: str | list[str], meta: object = None):
    self._write(LogLevel.ERROR, message, meta)

  def fatal(self, message: str | list[str], meta: object = None):
    self._write(LogLevel.FATAL, message, meta)


logger = Logger(LogLevel.TEST)