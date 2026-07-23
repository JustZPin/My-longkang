"""Unit tests for the drain-blockage waste classifier.

Run from the repo root with:  python -m pytest
(No camera or GStreamer needed — classify_waste is a pure function.)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ground_station.classifier import classify_waste  # noqa: E402


def test_paper_white():
    # Low saturation, high value -> white paper.
    assert classify_waste((0, 10, 220)) == "Paper (White)"


def test_aluminium_red():
    assert classify_waste((5, 200, 200)) == "Aluminium (Red)"
    # Red also wraps around the top of the hue circle.
    assert classify_waste((178, 200, 200)) == "Aluminium (Red)"


def test_aluminium_blue():
    assert classify_waste((120, 200, 200)) == "Aluminium (Blue)"


def test_glass_green():
    assert classify_waste((60, 150, 150)) == "Glass (Green)"


def test_glass_black():
    assert classify_waste((0, 10, 20)) == "Glass (Black)"


def test_other_yellow():
    assert classify_waste((30, 200, 200)) == "Other (Yellow)"


def test_other_waste_fallback():
    # A blue-ish hue but not saturated enough for any specific rule.
    assert classify_waste((100, 100, 100)) == "Other Waste"
