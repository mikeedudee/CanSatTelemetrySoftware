# CanSatTelemetrySoftware

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

Real-time data acquisition and visualization system designed specifically for our CanSat mission. It enables seamless communication between the onboard microcontroller and the ground station via radio telemetry, ensuring reliable transmission and logging of critical flight parameters throughout the mission profile.

---

## Table of Contents

1. [Features](#features)

## Features

- **Real-time serial-port telemetry**  
  - Auto-detect available COM ports  
  - Parse and validate 14 telemetry channels (pressure, GPS, attitude, etc.)  
  - Compute horizontal speed via Haversine formula  
- **Offline map integration**  
  - Pan/zoom over cached map tiles using `tkintermapview`  
  - Plot current GPS track & waypoints  
- **Responsive GUI**  
  - CustomTkinter theme & layout  
  - Configurable widgets, buttons, status indicators  
- **User authentication**  
  - Simple login screen with `bcrypt`-encrypted credentials  
- **Performance monitoring**  
  - Optional GPU acceleration via `cupy`  
  - System stats overlay using `psutil` & `GPUtil`  

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
