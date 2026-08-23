import math
import time

from utils.models import QR_Code, QRTrack
from settings import settings, shared



def is_plausible_qr_code(qr_code: QR_Code) -> bool:
    """Check whether detected corners satisfy the active QR geometry preset.

    Args:
        qr_code: Detected QR code whose four corners are evaluated.

    Returns:
        True when every active geometric threshold is satisfied.
    """
    
    preset = shared.get_validation_presets()[settings.validation_preset]
    
    points = qr_code.points

    top_left = points.top_left
    top_right = points.top_right
    bottom_right = points.bottom_right
    bottom_left = points.bottom_left

    top = math.dist(top_left, top_right)
    right = math.dist(top_right, bottom_right)
    bottom = math.dist(bottom_right, bottom_left)
    left = math.dist(bottom_left, top_left)

    side_lengths = [top, right, bottom, left]
    shortest_side = min(side_lengths)
    longest_side = max(side_lengths)

    if shortest_side < preset.min_side_px:
        return False
    
    if longest_side > preset.max_side_px:
        return False

    if longest_side / shortest_side > preset.max_adjacent_side_ratio:
        return False

    if max(top, bottom) / max(min(top, bottom), 1e-6) > preset.max_top_bottom_side_ratio:
        return False

    if max(left, right) / max(min(left, right), 1e-6) > preset.max_left_right_side_ratio:
        return False

    diagonal_a = math.dist(top_left, bottom_right)
    diagonal_b = math.dist(top_right, bottom_left)
    if max(diagonal_a, diagonal_b) / max(min(diagonal_a, diagonal_b), 1e-6) > preset.max_diagonal_ratio:
        return False

    vectors = [
        (top_right.x - top_left.x, top_right.y - top_left.y),
        (bottom_right.x - top_right.x, bottom_right.y - top_right.y),
        (bottom_left.x - bottom_right.x, bottom_left.y - bottom_right.y),
        (top_left.x - bottom_left.x, top_left.y - bottom_left.y),
    ]

    for index in range(4):
        first = vectors[index]
        second = vectors[(index + 1) % 4]

        first_length = math.hypot(first[0], first[1])
        second_length = math.hypot(second[0], second[1])
        if first_length == 0 or second_length == 0:
            return False

        dot = abs(first[0] * second[0] + first[1] * second[1]) / (first_length * second_length)
        if dot > preset.min_corner_dot:
            return False

    return True


class LongTermValidator:
    """Track QR detections over time before treating them as valid."""

    def __init__(self):
        """Create a validator with no active QR tracks."""
        self._tracks: list[QRTrack] = []
    
    @property
    def tracks(self):
        """Return active tracks with validated and recent tracks first.

        Returns:
            Sorted active QR tracks.
        """
        return sorted(self._tracks, key=lambda track: (not track.validated, -track.last_seen_at))

    def validate(self, qr_code: QR_Code) -> bool:
        """Update a matching track and report whether it is validated.

        Args:
            qr_code: Current plausible QR detection.

        Returns:
            True when the matching track has met validation requirements.
        """

        current_time = time.perf_counter()

        track = self._find_track(qr_code)

        if track is None:
            self._tracks.append(self._create_track(qr_code, current_time))
            return False

        track.center_x = qr_code.center_x
        track.center_y = qr_code.center_y
        track.radius = self._calc_radius(qr_code.size)
        track.last_seen_at = current_time
        track.appearances += 1

        if track.validated:
            self._remove_overlapping_invalid_tracks(track)
            return True

        if current_time - track.first_seen_at >= settings.long_term_validation_settings.period:
            if track.appearances >= settings.long_term_validation_settings.min_appearance:
                track.validated = True
                self._remove_overlapping_invalid_tracks(track)
                return True

            self._tracks.remove(track)

        return False

    def update(self):
        """Remove tracks that have expired under current validation settings."""
        self._cleanup(time.perf_counter())

    def _find_track(self, qr_code: QR_Code) -> QRTrack | None:
        """Find the best existing track overlapping a QR detection.

        Args:
            qr_code: QR detection to match against active tracks.

        Returns:
            Nearest matching track, preferring validated tracks, or None.
        """
        matching_tracks: list[QRTrack] = []

        for track in self._tracks:
            distance = math.hypot(
                qr_code.center_x - track.center_x,
                qr_code.center_y - track.center_y,
            )

            if distance <= track.radius:
                matching_tracks.append(track)

        if not matching_tracks:
            return None

        return min(
            matching_tracks,
            key=lambda track: (
                not track.validated,
                math.hypot(
                    qr_code.center_x - track.center_x,
                    qr_code.center_y - track.center_y,
                ),
            ),
        )

    def _create_track(self, qr_code: QR_Code, current_time: float) -> QRTrack:
        """Create an initial track for a new detection.

        Args:
            qr_code: QR detection that starts the track.
            current_time: Monotonic creation timestamp.

        Returns:
            Newly initialized QR track.
        """
        return QRTrack(
            center_x=qr_code.center_x,
            center_y=qr_code.center_y,
            radius=self._calc_radius(qr_code.size),
            first_seen_at=current_time,
            last_seen_at=current_time,
            appearances=1,
        )

    def _cleanup(self, current_time: float):
        """Discard expired validated and unvalidated tracks.

        Args:
            current_time: Monotonic timestamp used for expiry checks.
        """
        self._tracks = [
            track
            for track in self._tracks
            if (
                track.validated
                and current_time - track.last_seen_at <= settings.long_term_validation_settings.max_gap_time
            )
            or (
                not track.validated
                and current_time - track.first_seen_at < settings.long_term_validation_settings.period
            )
        ]

    def _remove_overlapping_invalid_tracks(self, valid_track: QRTrack):
        """Remove invalid tracks whose regions overlap a validated track.

        Args:
            valid_track: Validated track whose region takes precedence.
        """
        self._tracks = [
            track
            for track in self._tracks
            if track is valid_track
            or track.validated
            or not self._tracks_overlap(track, valid_track)
        ]

    def _tracks_overlap(self, first: QRTrack, second: QRTrack) -> bool:
        """Check whether two circular tracking regions intersect.

        Args:
            first: First tracking region.
            second: Second tracking region.

        Returns:
            True when the regions overlap or touch.
        """
        distance = math.hypot(
            first.center_x - second.center_x,
            first.center_y - second.center_y,
        )

        return distance <= first.radius + second.radius

    def _calc_radius(self, size: float):
        """Calculate tracking radius from QR side length.

        Args:
            size: Average QR side length in pixels.

        Returns:
            Tracking radius scaled by the configured distance multiplier.
        """
        # return settings.calibration_value / distance_cm / 2 * settings.long_term_validation_settings.dist_mult; same as:
        return size / 2 * settings.long_term_validation_settings.dist_mult

longTermValidator = LongTermValidator()
