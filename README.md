## ⚠️ Disclaimer 
> This repository contains a **preview version** of the Telemetry Software for our experimental rocket "Hanggang Sa Dulo".  
> Please note that this source code is **not finalized** and remains **under active development**.  
> **Unresolved bugs, incomplete features, and performance issues may occur.**
> 
> Use with caution and make sure to install all the dependencies, especially the required **CUDA version** for your system, so that it will run accordingly, as it may affect your hardware.

# CanSatTelemetrySoftware

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

Real-time data visualization system designed specifically for our CanSat mission. Communicates between the onboard microcontroller and the ground station via our radio communication module.

---

## Table of Contents

1. [Features](#features)
2. [Architecture & Module Layout](#architecture--module-layout)
3. [Prerequisites](#prerequisites)
4. [Installation & Dependencies](#installation)
5. [IMPORTANT!](#Note)
6. [Usage](#Usage)

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
  - Real-time 3-dimensional trajectory/flight-path projection
- **User authentication**  
  - Simple login screen with `bcrypt`-encrypted credentials  
- **Performance monitoring**  
  - Optional GPU acceleration via `cupy`  
  - System stats overlay using `psutil` & `GPUtil`  

---

## Architecture & Module Layout

We follow a **layered** structure mirroring clean-architecture principles:

- **`core/`** (Domain Logic)  
  - `geo_utils.py` ― Haversine & coordinate-conversion utilities   
- **`main`**  
  - `newui7_stable_rebuild_offlinemap.py` ― Main dashboard & map widgets  
  - `login.py` ― Login dialog and credential management
- **`assets`**
  - `CanSat Compe Logo.png` - Competition Logo
  - `Flag_of_the_Philippines.jpg` — Philippine Flag
  - `HsD Logo.png` - Our group's Logo
  - `hsd_logo_Fxh_icon.ico` — Software's Logo
  - `IAU Logo.png` - Our University's Logo
  - `syae.png` - Our department Logo
- **`assets\3dMeshes`**
    - `cylinder.stl` - For the Attitude Visualization 3d Object
      
---

## Prerequisites

- **OS:** Windows 10/11, macOS, or Linux  
- **Python:** ≥ 3.8 (3.9+)  
- **Hardware:**  
  - USB-serial adapter or onboard COM port  
  - GPU with CUDA support
    > Tested in an environment of CUDA Build: cuda_12.9.r12.9/compiler.35813241_0 (V12.9.41)
    > Incompatibility may occur at your instance.

---

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/mikeedudee/CanSatTelemetrySoftware.git
   cd CanSatTelemetrySoftware

2. **Dependencies**
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

* You can install them all at once using the command below:
  ```bash
  pip install customtkinter pyserial tkintermapview cupy psutil GPUtil matplotlib numpy numpy-stl memory-profiler bcrypt pywinstyles Pillow
  ```

* Or Install them with:
  ```bash
  pip install -r requirements.txt
  ```

---

## Note:
Ensure you’re using a compatible Python 3.x interpreter.
- For GPU acceleration, cupy must match your CUDA toolkit version.
- tkinter comes with the standard library, but on some Linux distributions you may need to install python3-tk.

---

## Usage:
**Before running the file make sure to install all the pre-requisites and make sure to have a compatible CUDA version installed on your system; otherwise, it will not work.**


To run, you can skip the login.py and go directly to the "newui7_stable_rebuild_offlinemap.py". If you wish to see it working and integrated into your system, your CanSat must provide the following format, or modify the reading formatting directly to suit your needs.
- **The Format**
  - `Pressure` ― Pressure reading from MS5611 or any sensor capable of providing such.
  - `Relative_Altitude` — Derived from the pressure data or simply from any data gathered from a sensor.
  - `Main Sensor Temperature` — From your main sensor reading of temperature.
  - `Backup Temperature` — From your backup temperature sensor.
  - `Latitude` — Latitude reading from the GPS.
  - `Longitude` — Longitude reading from the GPS.
  - `SD Card Status` — Must be 0 or 1 value.
  - `Elapsed Time` — Time starting from the initialization of the CanSat.
  - `Sensor Accurary` — Accurary state of your Inertial Measurement Unit (IMU) or any 9-DoF sensor (if capable).
  - `Yaw` — Yaw reading for your Inertial Measurement Unit (IMU).
  - `Pitch` — Pitch reading for your Inertial Measurement Unit (IMU).
  - `Roll` — Roll reading for your Inertial Measurement Unit (IMU).
  - `Velocity` — Vertical velocity reading (derived or accessed) from the sensor
  - `Absolute Altitude` — The fixed altitude from sea level.

---

**To make the GPS work offline, make sure you downloaded the maps of your place or the location of the launch site and run a python command line at that map JSON folder:**
  ```bash
  python -m http.server 8000
  ```

---

## How to download offline maps
- Download Mobile Atlas Creator

1. Select a Map Source:
    - Open MOBAC and choose the desired map source from the list (for example, OpenStreetMap, OpenCycleMap, etc.).
2. Define the Area:
    - Use the map view to navigate to the region you want to download tiles for. You can either draw a bounding box or select a predefined region.

3. Choose Zoom Levels:
    - In the interface, select the zoom levels you need. The more zoom levels you select, the larger (and more detailed) the downloaded atlas will be.

4. Select an Atlas Format:
    - Under the “Atlas Format” options, choose the format that suits your needs. For offline tile serving, you can select a “Tile Directory” (which saves tiles in a folder structure like {z}/{x}/{y}.png) or an MBTiles format if your offline viewer supports it.

5. Create the Atlas:
    - Click the “Create Atlas” button. MOBAC will download the tiles for the specified region and zoom levels and save them in your chosen format.

6. Serve the Tiles Locally:
    - If you select a tile directory, you can then run a local HTTP server (e.g., using Python’s http.server module) in that folder so your application can use them offline.
