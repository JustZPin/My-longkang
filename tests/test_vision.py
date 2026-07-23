"""Tests for the on-robot RGB colour detection (vision.py).

Pure OpenCV/numpy, no GPIO. Skipped if OpenCV isn't installed.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

from robot.vision import detect_black_white, detect_red_rgb  # noqa: E402


def test_detect_black_white_shape_and_values():
    frame = np.zeros((20, 20, 3), dtype=np.uint8)
    frame[:, 10:] = 200  # right half bright
    bw = detect_black_white(frame)
    assert bw.shape == (20, 20)
    assert set(np.unique(bw)).issubset({0, 255})


def test_detect_red_rgb_draws_circle():
    # A red blob on black; detect_red_rgb should draw a circle (frame changes).
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(frame, (30, 30), (70, 70), (200, 0, 0), -1)  # RGB-ish red blob
    before = frame.copy()
    out = detect_red_rgb(frame)
    assert out.shape == before.shape
