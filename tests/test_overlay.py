"""Tests for the overlay concern (centre HSV sampling).

Requires numpy + OpenCV. Skipped automatically if OpenCV isn't installed,
so the classifier tests still run in a headless/minimal environment.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

from ground_station.overlay import sample_center_hsv  # noqa: E402


def test_sample_center_hsv_solid_red():
    # Solid red BGR frame -> HSV hue ~0, high saturation, high value.
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :] = (0, 0, 255)  # BGR red
    h, s, v = sample_center_hsv(frame)
    assert h <= 5 or h >= 175
    assert s > 200
    assert v > 200


def test_sample_center_hsv_solid_white():
    frame = np.full((100, 100, 3), 255, dtype=np.uint8)
    h, s, v = sample_center_hsv(frame)
    assert s < 10
    assert v > 240
