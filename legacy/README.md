# legacy / archived code

Code kept for reference but **not part of the live pipeline**.

## `on_robot_rgb_vision.py`

The earlier **on-robot RGB colour detection** (`detect_red/green/blue_rgb`,
`highlight_color`, `detect_black_white`). It processed frames locally on the Pi.

The winning architecture instead **streams** the camera to the laptop
(`libcamera-vid` → UDP), where the **HSV** classifier
(`src/ground_station/classifier.py`) does the colour work. The Pi can't both
hand its camera to `libcamera-vid` and run this local OpenCV path at once, so
this module is unused in the streaming setup.

Colour classification now lives in **one place: HSV, on the laptop.**

`test_on_robot_rgb_vision.py` is the matching test, moved here too.
