#!/usr/bin/env bash
# Laptop side: view-only receive (no classification). Useful to confirm the
# stream works before running the Python ground station. Needs GStreamer.
gst-launch-1.0 udpsrc port=5002 caps="application/x-rtp,media=video,encoding-name=H264,payload=96,clock-rate=90000" buffer-size=800000 \
  ! rtph264depay ! avdec_h264 ! videoflip method=2 ! autovideosink
