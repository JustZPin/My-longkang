"""Drain-blockage waste classifier (VER5 logic).

Maps an average HSV colour value to a likely drain-blocking material.
Kept as a pure function so it can be unit-tested without a camera/stream.
"""

from typing import Sequence


def classify_waste(hsv: Sequence[int]) -> str:
    """Map an average HSV value to a drain-blockage material (from VER5).

    Args:
        hsv: A 3-element sequence of (hue, saturation, value), OpenCV ranges
            (H: 0-180, S: 0-255, V: 0-255).

    Returns:
        A human-readable material label.
    """
    h, s, v = hsv
    if s < 50 and v > 180:
        return "Paper (White)"
    if (0 <= h <= 20 or 170 <= h <= 180) and s > 120 and v > 80:
        return "Aluminium (Red)"
    if 90 <= h <= 150 and s > 120 and v > 80:
        return "Aluminium (Blue)"
    if 40 <= h <= 90 and s > 70 and v > 60:
        return "Glass (Green)"
    if s < 50 and v < 50:
        return "Glass (Black)"
    if 20 <= h <= 40 and s > 150 and v > 150:
        return "Other (Yellow)"
    return "Other Waste"
