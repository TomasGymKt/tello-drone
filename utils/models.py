import math
import threading
from dataclasses import asdict, dataclass
from typing import NamedTuple
from enum import StrEnum
from settings import settings


class Int_Vector2(NamedTuple):
    """Immutable two-dimensional integer coordinate."""
    x: int
    y: int


class Corners(NamedTuple):
    """Ordered QR-code corners: top-left, top-right, bottom-right, bottom-left."""
    top_left: Int_Vector2
    top_right: Int_Vector2
    bottom_right: Int_Vector2
    bottom_left: Int_Vector2


def qr_size(points: Corners) -> float:
    """Calculate the average side length of a quadrilateral.

    Args:
        points: Ordered corners of the quadrilateral.

    Returns:
        Average length of the four sides in pixels.
    """
    top = math.dist(points.top_left, points.top_right)
    right = math.dist(points.top_right, points.bottom_right)
    bottom = math.dist(points.bottom_right, points.bottom_left)
    left = math.dist(points.bottom_left, points.top_left)

    return (top + right + bottom + left) / 4


class QR_Code:
    """Detected QR code with geometry, payload, and distance measurements."""

    def __init__(self, points, text: str | None, frame):
        """Create QR measurements from detected corners and source frame.

        Args:
            points: Four detected corners ordered clockwise from top-left.
            text: Decoded payload, or None when decoding failed.
            frame: Source image used to calculate center error.
        """
        self.points = Corners(
            top_left=Int_Vector2(*points[0]),
            top_right=Int_Vector2(*points[1]),
            bottom_right=Int_Vector2(*points[2]),
            bottom_left=Int_Vector2(*points[3]),
        )
        self.text = text
        self.center_x = int(points[:, 0].mean())
        self.center_y = int(points[:, 1].mean())
        self.size = qr_size(self.points)
        self.distance_cm = settings.calibration_value / self.size
        self.error_x = self.center_x - frame.shape[1] // 2
        self.error_y = self.center_y - frame.shape[0] // 2

class SharedQR:
    """Thread-safe holder for the most recently validated QR code."""

    def __init__(self):
        """Create an empty synchronized QR-code holder."""
        self.lock = threading.Lock()
        self.qr_code: QR_Code | None = None

    def set(self, qr_code: QR_Code | None):
        """Replace the stored QR code.

        Args:
            qr_code: QR code to store, or None to clear it.
        """
        with self.lock:
            self.qr_code = qr_code

    def get(self):
        """Read the stored QR code.

        Returns:
            Latest stored QR code, or None when no code is available.
        """
        with self.lock:
            return self.qr_code


@dataclass(slots=True)
class ScanResult():
    """Outcome and timing metadata for one QR scan attempt."""
    success: bool = False
    in_validation: bool = False
    qr_code: QR_Code | None = None
    scan_method: str | None = None
    last_scan_ms: float | None = None
    last_scan_finished_at: float | None = None

class Padding:
    """Pixel padding with CSS-like shorthand defaults."""

    def __init__(self, top: int = 0, right: int | None = None, bottom: int | None = None, left: int | None = None):
        """Create padding values.

        Args:
            top: Top padding, or uniform padding when other sides are omitted.
            right: Right padding; defaults to top.
            bottom: Bottom padding; defaults to top.
            left: Left padding; defaults to right.
        """
        if right is None:
            right = top

        if bottom is None:
            bottom = top

        if left is None:
            left = right

        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
        
    @property
    def horizontal(self):
        """Return the combined left and right padding.

        Returns:
            Horizontal padding in pixels.
        """
        return self.left + self.right

    @property
    def vertical(self):
        """Return the combined top and bottom padding.

        Returns:
            Vertical padding in pixels.
        """
        return self.top + self.bottom


class Color(tuple):
    """Immutable BGR color accepted by OpenCV drawing functions."""

    def __new__(cls, *args):
        """Create a BGR color from a tuple or three channel values.

        Args:
            *args: A (blue, green, red) tuple or three channel values.

        Returns:
            Immutable BGR color tuple.

        Raises:
            ValueError: If arguments do not describe exactly three channels.
        """
        if len(args) == 1:
            color = args[0]

            if not isinstance(color, tuple) or len(color) != 3:
                raise ValueError("Color requires a (b, g, r) tuple")

            b, g, r = color

        elif len(args) == 3:
            b, g, r = args

        else:
            raise ValueError("Color requires (b, g, r) or b, g, r")

        return super().__new__(cls, (b, g, r))


class AlphaColor(Color):
    """BGR color with a separate alpha value for manual overlay blending."""

    def __new__(cls, *args):
        """Create an alpha color from BGR values and optional opacity.

        Args:
            *args: BGR tuple or channels, optionally followed by alpha.
                - b, g, r
                - (b, g, r)
                - b, g, r, a
                - (b, g, r), a

        Returns:
            Immutable BGR color carrying a separate alpha attribute.

        Raises:
            ValueError: If arguments do not describe a valid BGR color.
        """
        if len(args) == 1:
            color = args[0]
            alpha = 1.0

            if not isinstance(color, tuple) or len(color) != 3:
                raise ValueError("AlphaColor requires a (b, g, r) tuple")

            b, g, r = color

        elif len(args) == 2:
            color, alpha = args

            if not isinstance(color, tuple) or len(color) != 3:
                raise ValueError("AlphaColor requires a (b, g, r) tuple")

            b, g, r = color

        elif len(args) == 3:
            b, g, r = args
            alpha = 1.0

        elif len(args) == 4:
            b, g, r, alpha = args

        else:
            raise ValueError(
                "AlphaColor requires (b, g, r), b, g, r, ((b, g, r), alpha) or b, g, r, alpha"
            )

        return super().__new__(cls, b, g, r)

    def __init__(self, *args):
        """Store alpha supplied while constructing the BGR tuple.

        Args:
            *args: Construction arguments accepted by __new__.
        """
        if len(args) == 1 or len(args) == 3:
            self.alpha = 1.0
        elif len(args) == 2:
            self.alpha = args[1]
        else:
            self.alpha = args[3]


@dataclass(slots=True)
class MouseData:
    """Pointer coordinates and OpenCV mouse-event code."""
    x: int = -1
    y: int = -1
    event: int = -1


@dataclass(slots=True)
class ValidationPreset:
    """
    Parameter meaning:
    - **min_side_px**: shortest side must be at least this long; higher is stricter
    - **min_side_px**: longest side must be at most this long; lower is stricter
    - **max_top_bottom_side_ratio**: top vs bottom side mismatch; 1.0 means equal
    - **max_left_right_side_ratio**: left vs right side mismatch; 1.0 means equal
    - **max_adjacent_side_ratio**: longest side / shortest side; limits overall stretching
    - **max_diagonal_ratio**: mismatch between the two diagonals; lower is squarer
    - **min_corner_dot**: corner right-angle tolerance using normalized dot product; lower is stricter
    """
    
    min_side_px: float
    max_side_px: float
    max_top_bottom_side_ratio: float
    max_left_right_side_ratio: float
    max_adjacent_side_ratio: float
    max_diagonal_ratio: float
    min_corner_dot: float
    
    def to_dict(self) -> dict:
        """Convert validation thresholds into a JSON-serializable mapping.

        Returns:
            Dictionary containing every preset field.
        """
        return asdict(self)


@dataclass(slots=True)
class QRTrack:
    """State for one QR-code location tracked across scan frames."""
    center_x: float
    center_y: float
    radius: float

    first_seen_at: float
    last_seen_at: float

    appearances: int
    validated: bool = False
