# CanSatTelemetrySoftware

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

Real-time data acquisition and visualization system designed specifically for our CanSat mission. It enables seamless communication between the onboard microcontroller and the ground station via radio telemetry, ensuring reliable transmission and logging of critical flight parameters throughout the mission profile.


-- Dependencies
- customtkinter
- pyserial
- tkintermapview
- cupy
- psutil
- GPUtil
- matplotlib
- numpy
- numpy-stl
- memory-profiler
- bcrypt
- pywinstyles
- Pillow

You can install them all at once using the command below:

pip install customtkinter pyserial tkintermapview cupy psutil GPUtil matplotlib numpy numpy-stl memory-profiler bcrypt pywinstyles Pillow

## Note:
Ensure you’re using a compatible Python 3.x interpreter.
- For GPU acceleration, cupy must match your CUDA toolkit version.
- tkinter comes with the standard library, but on some Linux distributions you may need to install python3-tk.
