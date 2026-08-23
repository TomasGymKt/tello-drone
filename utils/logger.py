from enum import Enum
from datetime import datetime
from os import get_terminal_size
from textwrap import wrap
import re

ANSI_ESCAPE_RE = re.compile(
  r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
)


def strip_ANSI_escape_code(msg: str) -> str:
  """Remove ANSI terminal escape sequences from text.

  Args:
    msg: Text that may contain ANSI formatting sequences.

  Returns:
    Plain text with ANSI sequences removed.
  """
  return ANSI_ESCAPE_RE.sub("", msg)

class LogLevel(Enum):
  """Severity levels accepted by the project logger."""
  TEST = -1
  DEBUG = 0
  INFO = 1
  WARN = 2
  ERROR = 3
  FATAL = 4


LEVEL_COLORS = {
  LogLevel.TEST: "\033[92m",
  LogLevel.DEBUG: "\033[95m",
  LogLevel.INFO: "\033[96m",
  LogLevel.WARN: "\033[93m",
  LogLevel.ERROR: "\033[91m",
  LogLevel.FATAL: "\033[31m",
}

RESET = "\033[0m"

terminal_width = get_terminal_size().columns


def _left_align(message: str, prefix: str, prefix_len: int):
  """Wrap a log message with a left-aligned prefix.

  Args:
    message: Message to wrap.
    prefix: Prefix added to the first output line.
    prefix_len: Visible width of the prefix without ANSI codes.

  Returns:
    Formatted multi-line message.
  """
  indent = " " * prefix_len
  parts = []
  
  for i, line in enumerate(message.splitlines()):
    parts.extend(wrap(line, width=terminal_width, initial_indent=prefix if i == 0 else indent, subsequent_indent=indent))

  return "\n".join(parts)

def _right_align(message: str, prefix: str, prefix_len: int) -> str:
  """Wrap a log message with a right-aligned suffix prefix.

  Args:
    message: Message to wrap.
    prefix: Suffix added to the first output line.
    prefix_len: Visible width of the prefix without ANSI codes.

  Returns:
    Formatted multi-line message.
  """
  message_width = terminal_width - prefix_len
  unprocessed = message.splitlines()
  lines: list[str] = []
  
  for line in unprocessed:
    lines.extend(wrap(line, message_width))
  
  max_len = max(len(strip_ANSI_escape_code(line)) for line in lines)

  out = []
  
  for i, line in enumerate(lines):
    ANSI_offset = len(line)-len(strip_ANSI_escape_code(line))
    if i == 0:
      out.append(line.ljust(max_len + ANSI_offset).rjust(message_width + ANSI_offset) + prefix) 
    else:
      out.append(line.ljust(max_len + ANSI_offset).rjust(message_width + ANSI_offset)) 
  

  return "\n".join(out)


class Logger:
  """Small ANSI-aware console logger with configurable severity filtering."""

  def __init__(self, min_level: LogLevel = LogLevel.DEBUG, is_left_align = True):
    """Create a logger.

    Args:
      min_level: Lowest severity that should be printed.
      is_left_align: Whether timestamps and levels appear on the left.
    """
    self.min_level = min_level
    self.is_left_align = is_left_align

  def _should_log(self, level: LogLevel) -> bool:
    """Check whether a severity passes the configured filter.

    Args:
      level: Severity to evaluate.

    Returns:
      True when messages at this severity should be printed.
    """
    return level.value >= self.min_level.value

  def _format_message(
    self,
    level: LogLevel,
    message: str
  ) -> str:
    """Add timestamp, severity, color, and alignment to a message.

    Args:
      level: Severity used for the prefix and color.
      message: Text to format.

    Returns:
      ANSI-formatted log message.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")

    color = LEVEL_COLORS[level]
    level_text = f"{color}{level.name}{RESET}"
    
    if self.is_left_align:
      
      prefix = f"[{timestamp}] [{level_text}]: "
      prefix_len = len(prefix) - len(f"{color}{RESET}")
      
      return _left_align(message, prefix, prefix_len)
    
    
    prefix = f" :[{timestamp}] [{level_text}]"
    prefix_len = len(prefix) - len(f"{color}{RESET}")
    
    return _right_align(message, prefix, prefix_len)

  def _write(
    self,
    level: LogLevel,
    message: str,
    meta: object | None = None
  ) -> None:
    """Print a message when its severity passes the filter.

    Args:
      level: Severity used for filtering and formatting.
      message: Main message text.
      meta: Optional related object printed below the message.
    """
    if not self._should_log(level):
      return

    formatted = self._format_message(level, str(message))

    if level == LogLevel.FATAL:
      line = "=" * terminal_width
      print(f"\n{line}")
      print(formatted)
      
      if meta:
        print(meta)

      print(line)
      return

    print(formatted)

    if meta:
      print(meta)

  def test(self, message: str, meta: object = None):
    """Log a test-level message.

    Args:
      message: Message to print.
      meta: Optional related object to print below the message.
    """
    self._write(LogLevel.TEST, message, meta)

  def debug(self, message: str, meta: object = None):
    """Log a debug-level message.

    Args:
      message: Message to print.
      meta: Optional related object to print below the message.
    """
    self._write(LogLevel.DEBUG, message, meta)

  def info(self, message: str, meta: object = None):
    """Log an info-level message.

    Args:
      message: Message to print.
      meta: Optional related object to print below the message.
    """
    self._write(LogLevel.INFO, message, meta)

  def success(self, message: str, meta: object = None):
    """Log a green info-level success message.

    Args:
      message: Message to print.
      meta: Optional related object to print below the message.
    """
    self._write(LogLevel.INFO, f"\033[92m{message}{RESET}", meta)

  def warn(self, message: str, meta: object = None):
    """Log a warning-level message.

    Args:
      message: Message to print.
      meta: Optional related object to print below the message.
    """
    self._write(LogLevel.WARN, message, meta)

  def error(self, message: str, meta: object = None):
    """Log an error-level message.

    Args:
      message: Message to print.
      meta: Optional related object to print below the message.
    """
    self._write(LogLevel.ERROR, message, meta)

  def fatal(self, message: str, meta: object = None):
    """Log a fatal-level message inside a visual separator.

    Args:
      message: Message to print.
      meta: Optional related object to print below the message.
    """
    self._write(LogLevel.FATAL, message, meta)


logger = Logger(LogLevel.TEST)
