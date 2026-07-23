#!/usr/bin/env bash
# Robot (Pi) side: stream the camera as H.264 over RTP/UDP to the laptop.
# Matches ground_station on 192.168.121.254:5002. Run this on the Raspberry Pi.
libcamera-vid -t 0 --width 640 --height 480 -n --inline --codec h264 --profile baseline -o - \
  | gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 \
    ! udpsink host=192.168.121.254 port=5002
