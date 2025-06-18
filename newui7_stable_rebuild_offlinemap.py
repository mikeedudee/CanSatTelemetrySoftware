import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
import serial 
import serial.tools.list_ports
import math
from threading import Thread
from collections import deque 
import time 
import datetime
import queue
import tkintermapview
from tkinter.scrolledtext import ScrolledText
import tkinter as tk
import cupy as cp
import psutil
import GPUtil
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from stl import mesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import runpy
matplotlib.use("TkAgg")
import platform
from memory_profiler import profile
import sqlite3
import bcrypt

# LOCAL FUNCTION DEPENDENCIES
from core.geo_utils import haversine_distance
from core.conversionGeo_util import *

'''
import cProfile, pstats, io
pr = cProfile.Profile()
pr.enable()
'''

startup_start = time.perf_counter()

#Global defaults
Pressure             = 0.0
Relative_Altitude    = 0.0
MS5611_Temperature   = 0.0
Thermistor           = 0.0
Latitude             = 0.0
Longitude            = 0.0
Latitude_Pred        = 0.0
Longitude_Pred       = 0.0
SD_Card_Status       = 0.0
Time_Elapsed         = 0.0
BNO08x_Status        = 0.0
Yaw                  = 0.0
Pitch                = 0.0
Roll                 = 0.0
Velocity             = 0.0
Absolute_Altitude    = 0.0
Time_Elapsed_minute  = 0.0
latency              = 0.0
last_data_timestamp  = 0.0
cpu_usage            = 0.0
mem_usage            = 0.0
gpu_usage            = 0.0
computed_horiz_speed = 0.0
prev_lat             = None
prev_lon             = None
prev_time            = None
latest_data          = None
running              = False
current_port         = None
ser                  = None
dashboard_instance   = None
BAUD_RATE            = 9600 #Defaut BAUD RATE
COM_PORT             = "COM24" #Defaut COM PORT
data_buffer          = deque(maxlen=5)

# PATH OF THE FILE TO ITSELF SO IT IS DYNAMIC
ASSETS_PATH_IMG = Path(__file__).resolve().parent / "assets"
ASSETS_PATH_3D  = Path(__file__).resolve().parent / "assets/3dMeshes"
stl_mesh    = mesh.Mesh.from_file(ASSETS_PATH_3D / 'cylinder.stl')

# Constants
EarthRadius   = (((2 * 6378.1370) + 6356.7523) / 3) * 1000

# Create a global command queue for sending commands from GUI to serial_thread
command_queue = queue.Queue() 

def get_available_com_ports():
    """Return a list of available COM port device names."""
    return [port.device for port in serial.tools.list_ports.comports()]

def read_com_data(ser):
    global values, line
    try:
        line = ser.readline().decode('utf-8').strip()
        if not line:
            return None
    except Exception as e:
        raise RuntimeError("Error reading from COM port: " + str(e))
    
    values = line.split()
    if len(values) != 14:
        raise ValueError(f"Expected 14 values but got {len(values)}: {line}")
    
    return {
        "Pressure": float(values[0]),
        "Relative_Altitude": float(values[1]),
        "MS5611_Temperature": float(values[2]),
        "Thermistor": float(values[3]),
        "Latitude": float(values[4]),
        "Longitude": float(values[5]),
        "SD_Card_Status": float(values[6]),
        "Time_Elapsed": float(values[7]),
        "BNO08x_Status": float(values[8]),
        "Yaw": float(values[9]),
        "Pitch": float(values[10]),
        "Roll": float(values[11]),
        "Velocity": float(values[12]),
        "Absolute_Altitude":    float(values[13])
    }
def dashboard_func():
    if dashboard_instance is not None:
        dashboard_instance.receiving_data = False
        
def serial_thread():
    global prev_lat, prev_lon, prev_time, computed_horiz_speed, running, ser, last_data_timestamp, current_port

    current_port = None
    ser          = None

    while running:
        # Check if the COM port has changed or no connection exists.
        if COM_PORT != current_port or ser is None:
            if ser is not None:
                running = False
                dashboard_func()
                messagebox.showerror("UNKNOWN ERROR", f"Unknown error occured: Check connection or restart the software.")
                ser.close()
            try:
                ser = serial.Serial(COM_PORT, baudrate=BAUD_RATE, timeout=0)
                current_port = COM_PORT
                #print(f"Connected to new COM Port: {COM_PORT}")
            except serial.SerialException as e:
                dashboard_func()
                messagebox.showwarning("CONNECTION ERROR", f"Could not open port.")

        try:
            data = read_com_data(ser)
            
            if data is None:
                continue
            
            last_data_timestamp = time.time()

            global Pressure, Relative_Altitude, MS5611_Temperature, Thermistor
            global Latitude, Longitude, SD_Card_Status, Time_Elapsed
            global BNO08x_Status, Yaw, Pitch, Roll, Velocity, Absolute_Altitude

            Pressure           = data["Pressure"]
            Relative_Altitude  = data["Relative_Altitude"]
            MS5611_Temperature = data["MS5611_Temperature"]
            Thermistor         = data["Thermistor"]
            Latitude           = data["Latitude"]
            Longitude          = data["Longitude"]
            SD_Card_Status     = data["SD_Card_Status"]
            Time_Elapsed       = data["Time_Elapsed"]
            BNO08x_Status      = data["BNO08x_Status"]
            Yaw                = data["Yaw"]
            Pitch              = data["Pitch"]
            Roll               = data["Roll"]
            Velocity           = data["Velocity"]
            Absolute_Altitude  = data["Absolute_Altitude"]
            
            print(f"{Pressure}, {Relative_Altitude}, {MS5611_Temperature}, {Thermistor}, {Latitude}, {Longitude}, {SD_Card_Status}, {Time_Elapsed}, {BNO08x_Status}, {Yaw}, {Pitch}, {Roll}, {Velocity}, {Absolute_Altitude}, {current_port}, {BAUD_RATE}")

            current_time = time.time()
            if prev_lat is not None and prev_lon is not None and prev_time is not None:
                dt = current_time - prev_time
                if dt > 0:
                    dist = haversine_distance(prev_lat, prev_lon, Latitude, Longitude)
                    computed_horiz_speed = dist / dt
            prev_lat  = Latitude
            prev_lon  = Longitude
            prev_time = current_time

        except Exception as e:
            #print("Error:", e)
            running = False
            if ser is not None:
                ser.close()
            dashboard_func()
            messagebox.showerror("CONNECTION ERROR", f"Cannot connect to the device.")
            # Set the receiving flag to False via the dashboard instance.
                
        #time.sleep(0.5)
    if ser is not None:
        ser.close()
    dashboard_func()
    
class UserDatabase:
    def __init__(self, db_file="cacheInitialization.dll"):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.create_table()
        self.user_map = {}  # Dictionary mapping random user ID to (username, hashed_password)
        
    def get_all_users(self):
        """
        Retrieves all user records as a list of tuples (user_random_id, username).
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT user_random_id, username FROM users")
            results = cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print("Database error while retrieving users:", e)
            return []
        
    def create_table(self):
        """
        Creates a table for users if it does not already exist.
        An additional column 'user_random_id' stores the random 8-digit identifier.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password BLOB NOT NULL,
                    user_random_id INTEGER UNIQUE NOT NULL
                );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print("Error creating the users table:", e)
            raise
         
# --------------------------------------------------
# MAIN DASHBOARD CLASS
# --------------------------------------------------
class TelemetryDashboard:
    def __init__(self):
        global dashboard_instance
        dashboard_instance = self
        self.main_window = ctk.CTk()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.main_window.title("TeresaIV Telemetry Dashboard")
        self.main_window.iconbitmap(ASSETS_PATH_IMG / 'hsd_logo_Fxh_icon.ico')
        self.main_window.attributes("-fullscreen", True)
        self.main_window.grid_columnconfigure(0, weight=1)
        self.main_window.grid_rowconfigure(1, weight=1)
        
        # Top, Middle, Bottom frames
        self.top_frame    = ctk.CTkFrame(self.main_window)
        self.middle_frame = ctk.CTkFrame(self.main_window)
        self.bottom_frame = ctk.CTkFrame(self.main_window)
        
        self.top_frame.grid(row=0, 
                            column=0, 
                            padx=10, 
                            pady=5, 
                            sticky="nsew")
        
        self.middle_frame.grid(row=1, 
                               column=0, 
                               padx=10, 
                               pady=5, 
                               sticky="nsew")
        
        # Initialize flight path data arrays (bounded deques)
        self.x_data        = deque(maxlen=500)
        self.y_data        = deque(maxlen=500)
        self.z_data        = deque(maxlen=500)
        self.ref_lat       = None
        self.ref_lon       = None
        self.prev_altitude = None
        self.prev_alt_time = None
        
        self.receiving_data = False
        
        # EXECUTE MAIN FUNCTIONS FOR SECTIONS
        self.setup_top_section()
        self.setup_middle_section()
        self.setup_bottom_section()
        self.update_com_ports()
        self.update_ui()
        #Thread(target=self.update_ui, daemon=True).start()
        
        startup_time = time.perf_counter() - startup_start
        print(f"Stable Build Startup time: {startup_time:.4f} seconds")
        #system_info = platform.uname()
        #print(system_info)
    
    def setup_top_section(self):
        self.time_display(self.top_frame)
        self.pressure_sd_status(self.top_frame)
        self.speed_display(self.top_frame)
        self.Temperature_vis(self.top_frame)
        
    def setup_middle_section(self):
        self.attitude_widget(parent=self.middle_frame, row=0, column=0)
        self.gyro_widget(parent=self.middle_frame, row=0, column=1)
        self.gps_stat(parent=self.middle_frame, row=0, column=2)
        self.gps_map_widget(parent=self.middle_frame, row=1, column=0)
        self.gps_map_widget_pred(parent=self.middle_frame, row=2, column=0)
        self.pressure_line_chart_widget(self.middle_frame, row=1, column=1)
        self.altitude_line_chart_widget(self.middle_frame, row=1, column=2)
        self.absolute_relative_altitude(parent=self.middle_frame, row=2, column=1)
        self.Predicted_Landing_Location(parent=self.middle_frame, row=2, column=2)
        self.flight_path_3d_widget(parent=self.middle_frame, row=0, column=3)
        
        self.middle_frame.grid_columnconfigure(3, weight=1)
        self.middle_frame.grid_rowconfigure(0, weight=1)
        self.middle_frame.grid_rowconfigure(1, weight=1)
        self.middle_frame.grid_rowconfigure(2, weight=1)
        
    def setup_bottom_section(self):
        db = UserDatabase()
        self.main_window.grid_rowconfigure(2, weight=0)
        bottom_frame = ctk.CTkFrame(self.main_window)
        bottom_frame.grid(row = 2, 
                          column=0, 
                          sticky="ew", 
                          padx=10, 
                          pady=0)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        
        left_button_frame = ctk.CTkFrame(bottom_frame)
        left_button_frame.grid(row=0, 
                               column=0, 
                               sticky="w", 
                               padx=5, 
                               pady=5)
        
        # SAVE DATA BUTTON
        toggle_save_btn = ctk.CTkButton(
            left_button_frame,
            text="Save Data",
            command=self.toggle_save_data,
            width=120,
            #corner_radius=10,
            #fg_color="transparent",
            #hover_color="#00598b",
            #border_color="#FFCC70",
            #border_width=2
        )
        toggle_save_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # BUZZER BUTTON
        buzzer_btn = ctk.CTkButton(
            left_button_frame,
            text="Buzzer On/Off",
            command=self.toggle_buzzer,
            width=120
        )
        buzzer_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # ERASE DATA BUTTON
        erase_data_btn = ctk.CTkButton(
            left_button_frame,
            text="Erase Saved Data",
            command=self.erase_saved_data,
            width=120
        )
        erase_data_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # REBOOT DEVICE BUTTON
        reboot_btn = ctk.CTkButton(
            left_button_frame,
            text="REBOOT",
            command=self.reboot_device,
            width=120
        )
        reboot_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # START/STOP DATA RECEIVING BUTTON
        start_data_btn = ctk.CTkButton(
            left_button_frame,
            text="Start Receiving Data",
            command=self.start_receiving_data,
            width=140
        )
        start_data_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # STOP DATA RECEIVING BUTTON
        stop_data_btn = ctk.CTkButton(
            left_button_frame,
            text="Stop Receiving Data",
            command=self.stop_receiving_data,
            width=140
        )
        stop_data_btn.grid(row=1, column=4, padx=5, pady=5)
        
        # DYNAMIC PORT combo box
        self.com_port_label = ctk.CTkLabel(left_button_frame, text="COM Port:")
        self.com_port_label.grid(row=0, column=5, padx=5, pady=5)
        self.com_port_option = ctk.CTkComboBox(
            left_button_frame,
            command=self.choose_com_port,
            width=100
        )
        self.com_port_option.grid(row=0, column=6, padx=5, pady=5)
        self.com_port_option.set(COM_PORT)
        
        # DYNAMIC BAUD RATE combo box
        self.baud_rate_label = ctk.CTkLabel(left_button_frame, text="Baud Rate:")
        self.baud_rate_label.grid(row=1, column=5, padx=5, pady=5)
        self.baud_rate_option = ctk.CTkComboBox(
            left_button_frame, 
            values=["110", 
                    "300", 
                    "600", 
                    "1200", 
                    "2400", 
                    "4800", 
                    "9600", 
                    "14400", 
                    "19200", 
                    "38400", 
                    "57600", 
                    "115200", 
                    "128000", 
                    "2560000"],
            command=self.choose_baud_rate,
            width=100
        )
        self.baud_rate_option.grid(row=1, column=6, padx=5, pady=5)
        self.baud_rate_option.set(BAUD_RATE)
        
        # Right-side frame for other buttons
        right_button_frame = ctk.CTkFrame(bottom_frame)
        right_button_frame.grid(row=0, column=1, sticky="e", padx=10, pady=5)
        
        # RUN SYSTEM CHECK BUTTON
        #run_check_btn = ctk.CTkButton(
        #    right_button_frame,
        #    text="Run System Check",
        #    command=self.system_check,
        #    width=120
        #)
        #run_check_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # SESSION ID AND USERNAME
        '''users = db.get_all_users()
        if users:
            # Use the first user from the retrieved list.
            session_ID, session_username = users[0]
        else:
            session_ID = "Unknown"
            session_username = "Unknown"
            
        session_id_label = ctk.CTkLabel(
            right_button_frame,
            text=f"Session ID: {session_ID} | {session_username}",
            font=("Arial", 12),
            anchor="center"  # Center align the text
        )
        session_id_label.grid(row=0, column=1, columnspan=2, padx=5, pady=5)  # Span across two columns
        '''

        # LOGOUT BUTTON
        logout_btn = ctk.CTkButton(
            right_button_frame,
            text="LOGOUT",
            command=self.logout,
            width=80
        )
        logout_btn.grid(row=1, column=1, padx=5, pady=5)

        # EXIT APPLICATION BUTTON
        exit_btn = ctk.CTkButton(
            right_button_frame,
            text="EXIT",
            command=self.exit_app,
            fg_color="red",
            width=80
        )
        exit_btn.grid(row=1, column=2, padx=5, pady=5)

        
        copyright_text_1 = ctk.CTkLabel(
            left_button_frame,
            text="Copyright © 2025 Hanggang Sa Dulo – Third‑Year Students of the Aerospace Engineering Department, Indiana Aerospace University.",
            anchor="nw", 
            font=("Arial", 12, "italic")
        )
        copyright_text_1.grid(row=0, column=7, padx=10, pady=5)

        copyright_text_2 = ctk.CTkLabel(
            left_button_frame,
            text="Software developed, programmed, and designed by Francis Mike John Camogao. All rights reserved. buildv 7.8-4 — stable-build",
            anchor="nw", 
            font=("Arial", 12, "italic")
        )
        copyright_text_2.grid(row=1, column=7, padx=10, pady=5)

            
    # --------------------------------------------------
    # TOP SECTION
    # -------------------------------------------------- 
    def time_display(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(side="left", padx=10, pady=5, fill="both", expand=True)
        
        # Configure four columns (0 to 3)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(3, weight=1)
        
        current_time_header = ctk.CTkLabel(frame, text="CURRENT TIME", anchor="center", font=("Arial", 14, "bold"))
        current_time_header.grid(row=0, 
                                 column=0, 
                                 padx=2.5, 
                                 pady=5, 
                                 sticky="nsew")
        
        current_date_header = ctk.CTkLabel(frame, text="CURRENT DATE", anchor="center", font=("Arial", 14, "bold"))
        current_date_header.grid(row=0, 
                                 column=1, 
                                 padx=2.5, 
                                 pady=5, 
                                 sticky="nsew")
        
        elapsed_time_header = ctk.CTkLabel(frame, text="RUN TIME", anchor="center", font=("Arial", 14, "bold"))
        elapsed_time_header.grid(row=0, 
                                 column=2, 
                                 columnspan=2, 
                                 padx=2.5, 
                                 pady=5, 
                                 sticky="nsew")
        
        self.current_time_label = ctk.CTkLabel(frame, text="", anchor="center")
        self.current_time_label.grid(row=1, 
                                     column=0, 
                                     )
        
        self.current_date_label = ctk.CTkLabel(frame, text="", anchor="center")
        self.current_date_label.grid(row=1, 
                                     column=1, 
                                     padx=5, 
                                     pady=5, 
                                     sticky="nsew")
        
        self.elapsed_time_label = ctk.CTkLabel(frame, text=f"{Time_Elapsed}", anchor="center")
        self.elapsed_time_label.grid(row=1, 
                                     column=2, 
                                     padx=5, 
                                     pady=5, 
                                     sticky="nsew")
        
        self.elapsed_time__minute_label = ctk.CTkLabel(frame, text=f"{Time_Elapsed_minute}", anchor="center")
        self.elapsed_time__minute_label.grid(row=1, 
                                             column=3, 
                                             padx=5, 
                                             pady=5, 
                                             sticky="nsew")
        
    def pressure_sd_status(self, parent):
        global Pressure, SD_Card_Status
        frame = ctk.CTkFrame(parent)
        frame.pack(side="left", padx=10, pady=5, fill="both", expand=True)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        pressure_header = ctk.CTkLabel(frame, text="PRESSURE", anchor="center", font=("Arial", 14, "bold"))
        pressure_header.grid(row=0, 
                             column=0, 
                             padx=5, 
                             pady=5, 
                             sticky="nsew")
        
        sd_header = ctk.CTkLabel(frame, text="SD CARD STATUS", anchor="center", font=("Arial", 14, "bold"))
        sd_header.grid(row=0, 
                       column=1, 
                       padx=5, 
                       pady=5, 
                       sticky="nsew")
        
        self.pressure_label = ctk.CTkLabel(frame, text=f"{Pressure}", anchor="center")
        self.pressure_label.grid(row=1, 
                                 column=0, 
                                 padx=5, 
                                 pady=5, 
                                 sticky="nsew")
        
        self.sd_status_label = ctk.CTkLabel(frame, text=f"{SD_Card_Status}", anchor="center")
        self.sd_status_label.grid(row=1, 
                                  column=1, 
                                  padx=5, 
                                  pady=5, 
                                  sticky="nsew")
        
    def speed_display(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(side="left", padx=10, pady=5, fill="both", expand=True)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        horiz_header = ctk.CTkLabel(frame, text="HORIZONTAL SPEED", anchor="center", font=("Arial", 14, "bold"))
        horiz_header.grid(row=0, 
                          column=0, 
                          padx=5,
                          pady=5,
                          sticky="nsew")
        
        vert_header = ctk.CTkLabel(frame, text="VERTICAL SPEED", anchor="center", font=("Arial", 14, "bold"))
        vert_header.grid(row=0, 
                         column=1,
                         padx=5,
                         pady=5,
                         sticky="nsew")
        
        self.horiz_speed_label = ctk.CTkLabel(frame, text=f"{computed_horiz_speed:.2f}", anchor="center")
        self.horiz_speed_label.grid(row=1,
                                    column=0,
                                    padx=5,
                                    pady=5,
                                    sticky="nsew")
        
        self.vert_speed_label = ctk.CTkLabel(frame, text=f"{Relative_Altitude:.2f}", anchor="center")
        self.vert_speed_label.grid(row=1, 
                                   column=1,
                                   padx=5, 
                                   pady=5, 
                                   sticky="nsew")
    
    def Temperature_vis(self, parent):
        global MS5611_Temperature, Thermistor
        frame = ctk.CTkFrame(parent)
        frame.pack(side="left", padx=10, pady=5, fill="both", expand=True)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        temp_header = ctk.CTkLabel(frame, text="MS5611 TEMP", anchor="center", font=("Arial", 14, "bold"))
        temp_header.grid(row=0, 
                         column=0,
                         padx=5, 
                         pady=5,
                         sticky="nsew")
        
        therm_header = ctk.CTkLabel(frame, text="THERMISTOR", anchor="center", font=("Arial", 14, "bold"))
        therm_header.grid(row=0, 
                          column=1,
                          padx=5,
                          pady=5,
                          sticky="nsew")
        
        self.temp_label = ctk.CTkLabel(frame, text=f"{MS5611_Temperature:.2f}", anchor="center")
        self.temp_label.grid(row=1, 
                             column=0,
                             padx=5, 
                             pady=5, 
                             sticky="nsew")
        
        self.thermistor_label = ctk.CTkLabel(frame, text=f"{Thermistor:.2f}", anchor="center")
        self.thermistor_label.grid(row=1, 
                                   column=1,
                                   padx=5,
                                   pady=5, 
                                   sticky="nsew")
        
    # --------------------------------------------------
    # MIDDLE SECTION
    # -------------------------------------------------- 
    def attitude_widget(self, parent, row, column):
        self.attitude_frame = ctk.CTkFrame(parent)
        self.attitude_frame.grid(row=row, 
                                 column=column,
                                 padx=10,
                                 pady=10, 
                                 sticky="nsew")
        self.fig = plt.Figure(figsize=(4, 4), dpi=100)
        self.ax  = self.fig.add_subplot(111, projection='3d')
        self.ax.set_title("CanSat Attitude")
        self.ax.set_xlim([-1, 1])
        self.ax.set_ylim([-1, 1])
        self.ax.set_zlim([-1, 1])
        self.ax.set_xlabel("X: ")
        self.ax.set_ylabel("Y: ")
        self.ax.set_zlabel("Z: ")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.attitude_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.faces_array = stl_mesh.vectors.copy()  # Get the faces of the STL model

        # Center and scale the model to fit into the widget view
        min_coords       = self.faces_array.min(axis=(0, 1))
        max_coords       = self.faces_array.max(axis=(0, 1))
        center           = (min_coords + max_coords) / 2.0
        scale            = (max_coords - min_coords).max()
        self.faces_array = (self.faces_array - center) / scale * 1

        # Create the Poly3DCollection and add it to the 3D axis
        self.surface = Poly3DCollection(self.faces_array.tolist(), facecolor="orange", edgecolor="k", alpha=1)
        self.ax.add_collection3d(self.surface)  
        
    def rotation_matrix(self, roll, pitch, yaw):
        """
        Create a rotation matrix from roll, pitch, yaw angles (in radians).
        """
        Rx = np.array([[1, 0, 0],
                       [0, np.cos(roll), -np.sin(roll)],
                       [0, np.sin(roll), np.cos(roll)]])
        
        Ry = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                       [0, 1, 0],
                       [-np.sin(pitch), 0, np.cos(pitch)]])
        
        Rz = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                       [np.sin(yaw), np.cos(yaw), 0],
                       [0, 0, 1]])
        
        return Rz @ Ry @ Rx
    
    def gyro_widget(self, parent, row, column):
        global Latitude, Longitude
        self.gyro_widge = ctk.CTkFrame(parent)
        self.gyro_widge.grid(row=row,
                             column=column, 
                             padx=10,
                             pady=10,
                             sticky="nsew")

        gyro_header = ctk.CTkLabel(self.gyro_widge, text="GYROSCOPIC ATTITUDE", anchor="w", font=("Arial", 14, "bold"))
        gyro_header.pack(anchor="w",padx=5, pady=5)
        
        self.x_label = ctk.CTkLabel(self.gyro_widge, text="X", anchor="w")
        self.x_label.pack(anchor="w", padx=5, pady=2)
        
        self.y_label = ctk.CTkLabel(self.gyro_widge, text="Y", anchor="w")
        self.y_label.pack(anchor="w", padx=5, pady=2)
        
        self.z_label = ctk.CTkLabel(self.gyro_widge, text="Z", anchor="w")
        self.z_label.pack(anchor="w", padx=5,pady=2)
        
        self.sensor_status = ctk.CTkLabel(self.gyro_widge, text="Sensor Status:", anchor="w")
        self.sensor_status.pack(anchor="w", padx=5, pady=5)
        
        # Create a Matplotlib figure and axis.
        self.fig_speed_hori = plt.Figure(figsize=(4, 2), dpi=80)
        self.ax_speed_hori  = self.fig_speed_hori.add_subplot(111)
        self.ax_speed_hori.set_title("Horizontal Speed")
        self.ax_speed_hori.grid(True)
        
        # Two line objects for horizontal and vertical speeds.
        self.line_horiz_speed, = self.ax_speed_hori.plot([], [], label="Horizontal Speed")
        
        # Embed the figure into the CustomTkinter frame.
        self.canvas_speed_hori = FigureCanvasTkAgg(self.fig_speed_hori, master=self.gyro_widge)
        self.canvas_speed_hori.get_tk_widget().pack(fill="both", expand=True)
        
        # Initialize deques to store time and speed data.
        self.horiz_speed_time = deque(maxlen=500)
        self.horiz_speed_data = deque(maxlen=500)
        
        # Variables to compute vertical speed (change in Relative_Altitude).
        self.prev_speed_time_hori = None
        
    def gps_stat(self, parent, row, column):
        global Latitude, Longitude
        self.gps_status = ctk.CTkFrame(parent)
        self.gps_status.grid(row=row, 
                             column=column,
                             padx=10, 
                             pady=10,
                             sticky="nsew")
        
        gps_header = ctk.CTkLabel(self.gps_status, text="GPS", anchor="w", font=("Arial", 14, "bold"))
        gps_header.pack(anchor="w", padx=5, pady=5)
        
        self.latitude = ctk.CTkLabel(self.gps_status, text="Latitude:", anchor="w")
        self.latitude.pack(anchor="w", padx=5, pady=2)
        
        self.longitude = ctk.CTkLabel(self.gps_status, text="Longitude:", anchor="w")
        self.longitude.pack(anchor="w", padx=5, pady=2)
        
        self.latitude2 = ctk.CTkLabel(self.gps_status, text=" ", anchor="w")
        self.latitude2.pack(anchor="w", padx=5, pady=2)
        
        self.longitude2 = ctk.CTkLabel(self.gps_status, text=" ", anchor="w")
        self.longitude2.pack(anchor="w", padx=5, pady=5)
        
        # Create a Matplotlib figure and axis.
        self.fig_speed_ver = plt.Figure(figsize=(4, 2), dpi=80)
        self.ax_speed_vert = self.fig_speed_ver.add_subplot(111)
        self.ax_speed_vert.set_title("Vertical Speed")
        self.ax_speed_vert.grid(True)
        
        # Two line objects for horizontal and vertical speeds.
        self.line_vert_speed, = self.ax_speed_vert.plot([], [], label="Vertical Speed")
        
        # Embed the figure into the CustomTkinter frame.
        self.canvas_speed_vert = FigureCanvasTkAgg(self.fig_speed_ver, master=self.gps_status)
        self.canvas_speed_vert.get_tk_widget().pack(fill="both", expand=True)
        
        # Initialize deques to store time and speed data.
        self.vert_speed_time = deque(maxlen=500)
        self.vert_speed_data = deque(maxlen=500)
        
        # Variables to compute vertical speed (change in Relative_Altitude).
        self.prev_speed_time         = None
        self.prev_altitude_for_speed = None
        
    def gps_map_widget(self, parent, row, column):
        self.gps_map_frame = ctk.CTkFrame(parent)
        self.gps_map_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        
        self.map_widget = tkintermapview.TkinterMapView(
                                                        self.gps_map_frame,
                                                        width=400,
                                                        height=300,
                                                        corner_radius=0
                                                        )
                                                        
        self.map_widget.set_tile_server("http://localhost:8000/{z}/{x}/{y}.png")
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_position(Latitude, Longitude)
        self.map_widget.set_zoom(16)
        self.map_marker = self.map_widget.set_marker(Latitude, Longitude, text="Current Position")


    def pressure_line_chart_widget(self, parent, row, column):
        self.press_chart_frame = ctk.CTkFrame(parent)
        self.press_chart_frame.grid(row=row, 
                                    column=column, 
                                    padx=10, 
                                    pady=10, 
                                    sticky="nsew")
        
        self.fig_press = plt.Figure(figsize=(4, 2), dpi=80)
        self.ax_press = self.fig_press.add_subplot(111)
        self.ax_press.set_title("Pressure")
        self.ax_press.set_xlabel("Time (ms)")
        self.ax_press.set_ylabel("Pressure (Pa)")
        self.ax_press.grid(True)
        
        self.press_line, = self.ax_press.plot([], [], label="Pressure")
        #self.ax_press.legend()
        
        self.canvas_press = FigureCanvasTkAgg(self.fig_press, master=self.press_chart_frame)
        self.canvas_press.get_tk_widget().pack(fill="both", expand=True)
        
        self.press_time_history = deque(maxlen=500)
        self.press_data_history = deque(maxlen=500)

    def altitude_line_chart_widget(self, parent, row, column):
        self.alt_chart_frame = ctk.CTkFrame(parent)
        self.alt_chart_frame.grid(row=row,
                                  column=column, 
                                  padx=10, 
                                  pady=10, 
                                  sticky="nsew")
        
        self.fig_alt = plt.Figure(figsize=(4, 2), dpi=80)
        self.ax_alt  = self.fig_alt.add_subplot(111)
        self.ax_alt.set_title("Relative Altitude")
        self.ax_alt.set_xlabel("Time (ms)")
        self.ax_alt.set_ylabel("Altitude (m)")
        self.ax_alt.grid(True)
        
        self.alt_line, = self.ax_alt.plot([], [], label="Altitude")
        #self.ax_alt.legend()
        
        self.canvas_alt = FigureCanvasTkAgg(self.fig_alt, master=self.alt_chart_frame)
        self.canvas_alt.get_tk_widget().pack(fill="both", expand=True)
        
        self.alt_time_history = deque(maxlen=500)
        self.alt_data_history = deque(maxlen=500)
        
    def gps_map_widget_pred(self, parent, row, column):
        self.gps_map_frame_pred = ctk.CTkFrame(parent)
        self.gps_map_frame_pred.grid(row=row, 
                                     column=column,
                                     padx=10,
                                     pady=10, 
                                     sticky="nsew")
        
        self.map_widget_pred = tkintermapview.TkinterMapView(self.gps_map_frame_pred, 
                                                             width=300, 
                                                             height=200, 
                                                             corner_radius=0)
        self.map_widget_pred.set_tile_server("http://localhost:8000/{z}/{x}/{y}.png")
        self.map_widget_pred.pack(fill="both", expand=True)
        self.map_widget_pred.set_position(Latitude_Pred, Longitude_Pred)
        self.map_widget_pred.set_zoom(16)
        self.map_marker_pred = self.map_widget_pred.set_marker(Latitude_Pred, Longitude_Pred, text="Predicted Position")

    def absolute_relative_altitude(self, parent, row, column):
        global Absolute_Altitude, Relative_Altitude
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, 
                   column=column, 
                   padx=10, 
                   pady=10, 
                   sticky="nsew")
        
        # Configure two equally weighted columns for absolute and relative altitude
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        # Row 0: Headers for Absolute and Relative Altitude
        absolute_header = ctk.CTkLabel(frame, text="ABSOLUTE ALTITUDE", anchor="center", font=("Arial", 14, "bold"))
        absolute_header.grid(row=0, 
                             column=0, 
                             padx=5, 
                             pady=5, 
                             sticky="nsew")
        
        relative_header = ctk.CTkLabel(frame, text="RELATIVE ALTITUDE", anchor="center", font=("Arial", 14, "bold"))
        relative_header.grid(row=0, 
                             column=1, 
                             padx=5, 
                             pady=5, 
                             sticky="nsew")
        
        # Row 1: Values for Absolute and Relative Altitude
        self.absolute_label = ctk.CTkLabel(frame, text=f"{Absolute_Altitude}", anchor="center")
        self.absolute_label.grid(row=1, 
                                 column=0, 
                                 padx=5, 
                                 pady=5, 
                                 sticky="nsew")
        
        self.relative_label = ctk.CTkLabel(frame, text=f"{Relative_Altitude}", anchor="center")
        self.relative_label.grid(row=1, 
                                 column=1, 
                                 padx=5, 
                                 pady=5, 
                                 sticky="nsew")
        
        # Row 2: Latency Header spanning both columns
        latency_header = ctk.CTkLabel(frame, text="DATA INPUT TO VISUAL LATENCY", anchor="center", font=("Arial", 14, "bold"))
        latency_header.grid(row=2, 
                            column=0, 
                            columnspan=2, 
                            padx=5, 
                            pady=5, 
                            sticky="nsew")
        
        # Row 3: Latency Value spanning both columns and centered
        self.latency_label = ctk.CTkLabel(frame, text=f"{latency}", anchor="center")
        self.latency_label.grid(row=3, 
                                column=0, 
                                columnspan=2, 
                                padx=5, 
                                pady=5, 
                                sticky="nsew")

    def Predicted_Landing_Location(self, parent, row, column):
        frame              = ctk.CTkFrame(parent)
        self.predicted_lat = None
        self.predicted_lon = None   
        frame.grid(row=row, 
                   column=column, 
                   padx=10, 
                   pady=10, 
                   sticky="nsew")
        
        # Configure two equally weighted columns for absolute and relative altitude
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        battery_label = ctk.CTkLabel(frame, text="PREDICTED LANDING LOCATION", anchor="w", font=("Arial", 14, "bold"))
        battery_label.grid(row=0, 
                           column=0, 
                           padx=5,
                           pady=2, 
                           sticky="nsew")
        
        self.latitude_predict = ctk.CTkLabel(frame, text="Latitude:", anchor="w")
        self.latitude_predict.grid(row=1, 
                                   column=0, 
                                   padx=5, 
                                   pady=0, 
                                   sticky="nsew")
        
        self.longitude_predict = ctk.CTkLabel(frame, text="Longitude:", anchor="w")
        self.longitude_predict.grid(row=2, 
                                    column=0, 
                                    padx=5, 
                                    pady=0, 
                                    sticky="nsew")
        
        self.cpu_usage = ctk.CTkLabel(frame, text="CPU Usage:", anchor="w")
        self.cpu_usage.grid(row=3,
                            column=0,
                            padx=5,
                            pady=0,
                            sticky="nsew")
        
        self.gpu_usage = ctk.CTkLabel(frame, text="GPU Usage:", anchor="w")
        self.gpu_usage.grid(row=4,
                            column=0,
                            padx=5,
                            pady=0,
                            sticky="nsew")
        
        self.ram_usage = ctk.CTkLabel(frame, text="RAM Usage:", anchor="w")
        self.ram_usage.grid(row=5, 
                            column=0,
                            padx=5,
                            pady=0,
                            sticky="nsew")
       
    def flight_path_3d_widget(self, parent, row, column):
        self.flight_path_frame = ctk.CTkFrame(parent)
        self.flight_path_frame.grid(row=row, column=column,
                                    rowspan=3,
                                    padx=10, pady=10,
                                    sticky="nsew")

        self.fig_flight = plt.Figure(figsize=(7, 5), dpi=100)
        self.ax_flight  = self.fig_flight.add_subplot(111, projection='3d')
        self.ax_flight.set_title("CanSat Flight Path")
        self.ax_flight.set_xlabel("East/West (m)")
        self.ax_flight.set_ylabel("North/South (m)")
        self.ax_flight.set_zlabel("Altitude (m)")
        
        self.canvas_flight = FigureCanvasTkAgg(self.fig_flight, master=self.flight_path_frame)
        self.canvas_flight.get_tk_widget().pack(fill="both", expand=True)
        
    def update_ui(self):
        global last_data_timestamp, latency, ser
        try:
            t_now = time.time()
            current_time = t_now * 1000
            
            if self.receiving_data:
                
                ''' PRESSURE STATE '''
                if Pressure == 393221:
                    status_press = "Abnormal Data"
                    status_press_color = "red"
                elif ser is None or not ser.is_open:
                    status_press = "NDA"
                    status_press_color = "orange"
                else:
                    status_press = f"{Pressure:,} Pa"
                    status_press_color = "white"
                self.pressure_label.configure(text=status_press, text_color=status_press_color)

                ''' SD CARD STATUS '''
                if ser is None or not ser.is_open or SD_Card_Status == 0:
                    status_sd       = "404 Micro-SD Card" 
                    status_sd_color = "red"
                else:
                    status_sd       = "Active"
                    status_sd_color = "green"
                self.sd_status_label.configure(text=status_sd, text_color=status_sd_color)
                
                ''' HORIZONTAL AND VERTICAL STATUS '''
                if ser is None or not ser.is_open:
                    status_hori = "NDA"
                    status_hori_color = "orange"
                    status_vert = "NDA"
                    status_vert_color = "orange"
                else:
                    status_hori = f"{computed_horiz_speed:.4f} m/s"
                    status_hori_color = "white"
                    status_vert = f"{Relative_Altitude:.4f} m/s"
                    status_vert_color = "white"
                self.horiz_speed_label.configure(text=status_hori, text_color=status_hori_color)
                self.vert_speed_label.configure(text=status_vert, text_color=status_vert_color)
                
                ''' TEMPERATURES STATUS '''
                if MS5611_Temperature == -278.15:
                    status_ms5611 = f"Abnormal Temperature {MS5611_Temperature} C"
                    status_ms5611_color = "red"
                elif MS5611_Temperature == -10:
                    status_ms5611 = f"Minimum Temperature {MS5611_Temperature}C"
                    status_ms5611_color = "skyblue"
                elif MS5611_Temperature >= 60:
                    status_ms5611 = f"Maximum Temperature {MS5611_Temperature} C"
                    status_ms5611_color = "orange"
                elif MS5611_Temperature >= 70:
                    status_ms5611 = f"Critial Operating Temperature {MS5611_Temperature} C"
                    status_ms5611_color = "orange-red"
                elif ser is None or not ser.is_open:
                    status_ms5611 = "NDA"
                    status_ms5611_color = "orange"
                    status_thermis = "NDA"
                    status_thermis_color = "orange"
                else:
                    status_ms5611 = f"{MS5611_Temperature:.4f} C"
                    status_thermis = f"{Thermistor:.4f} C"
                    status_ms5611_color = "white"
                    status_thermis_color = "white"
                self.temp_label.configure(text=status_ms5611, text_color=status_ms5611_color)
                self.thermistor_label.configure(text=status_thermis, text_color=status_thermis_color)
            
                ''' RUN TIME STATUS '''
                current_time_str = datetime.datetime.now().strftime("%H:%M:%S")
                current_date_str = datetime.datetime.now().strftime("%m/%d/%Y")
                self.current_time_label.configure(text=current_time_str)
                self.current_date_label.configure(text=current_date_str)
                
                if ser is None or not ser.is_open:
                    status_time_run       = "NDA"
                    status_time_min       = "NDA"
                    status_time_run_color = "orange"
                    status_time_min_color = "orange"
                else:
                    status_time_run       = f"{Time_Elapsed:.0f} sec"
                    Time_Elapsed_minute   = Time_Elapsed / 60
                    status_time_min       = f"{Time_Elapsed_minute:.2f} min"
                    status_time_run_color = "white"
                    status_time_min_color = "white"
                self.elapsed_time_label.configure(text=status_time_run, text_color=status_time_run_color)
                self.elapsed_time__minute_label.configure(text=status_time_min, text_color=status_time_min_color)
            
                ''' ATTITUDE ALGORITHM '''
                roll_rad  = np.radians(Roll)
                pitch_rad = np.radians(Pitch)
                yaw_rad   = np.radians(Yaw)
                R         = self.rotation_matrix(roll_rad, pitch_rad, yaw_rad)
                
                # Extract body axes from the rotation matrix (using its columns)
                x_axis = R[:, 0]
                y_axis = R[:, 1]
                z_axis = R[:, 2]
                
                if hasattr(self, 'quiver_x'): # Remove previous quiver arrows if they exist
                    self.quiver_x.remove()
                    self.quiver_y.remove()
                    self.quiver_z.remove()

                # Draw the body axes using quiver arrows
                self.quiver_x = self.ax.quiver(0, 0, 0, x_axis[0], x_axis[1], x_axis[2], color='r', length=1, normalize=True)
                self.quiver_y = self.ax.quiver(0, 0, 0, y_axis[0], y_axis[1], y_axis[2], color='g', length=1, normalize=True)
                self.quiver_z = self.ax.quiver(0, 0, 0, z_axis[0], z_axis[1], z_axis[2], color='b', length=1, normalize=True)
                
                try: # Rotate the STL faces; use GPU acceleration if available
                    R_gpu         = cp.asarray(R)
                    faces_gpu     = cp.asarray(self.faces_array)
                    rotated_faces = cp.asnumpy(cp.dot(faces_gpu, R_gpu.T))
                except ImportError:
                    rotated_faces = np.dot(self.faces_array, R.T)
                
                self.surface.set_verts(rotated_faces.tolist())
                self.canvas.draw()
            
                ''' ATTITUDE STATUS '''
                if ser is None or not ser.is_open:
                    status_attitude_yaw         = "NDA"
                    status_attitude_pitch       = "NDA"
                    status_attitude_roll        = "NDA"
                    status_attitude_sense       = "NDA"
                    status_attitude_yaw_color   = "orange"
                    status_attitude_pitch_color = "orange"
                    status_attitude_roll_color  = "orange"
                    status_attitude_sense_color = "orange"
                else:
                    status_attitude_yaw         = f"{Yaw:.4f}"
                    status_attitude_pitch       = f"{Pitch:.4f}"
                    status_attitude_roll        = f"{Roll:.4f}"
                    status_attitude_sense       = f"{BNO08x_Status:.0f}"
                    status_attitude_yaw_color   = "white"
                    status_attitude_pitch_color = "white"
                    status_attitude_roll_color  = "white"
                    status_attitude_sense_color = "white"
                    
                self.sensor_status.configure(text=f"Sensor Accuracy: {status_attitude_sense}", text_color=status_attitude_sense_color)
                self.x_label.configure(text=f"Roll:  {status_attitude_yaw}", text_color=status_attitude_yaw_color)
                self.y_label.configure(text=f"Yaw: {status_attitude_pitch}", text_color=status_attitude_pitch_color)
                self.z_label.configure(text=f"Pitch:    {status_attitude_roll}", text_color=status_attitude_roll_color)
                
                ''' GPS WIDGET STATUS '''
                if ser is None or not ser.is_open:
                    status_lat       = "NDA"
                    status_lon       = "NDA"
                    status_lat_color = "orange"
                    status_lon_color = "orange"
                elif Latitude == 0 and Longitude == 0:
                    status_lat       = "   Invalid Data Available"
                    status_lon       = "Invalid Data Available"
                    status_lat_color = "orange"
                    status_lon_color = "orange"
                else:
                    status_lat       = f"{Latitude:.8f}"
                    status_lon       = f"{Longitude:.8f}"
                    status_lat_color = "white"
                    status_lon_color = "white"
                self.latitude.configure(text=f"Latitude:   {status_lat}", text_color=status_lat_color)
                self.longitude.configure(text=f"Longitude: {status_lon}", text_color=status_lon_color)
                self.latitude2.configure(text=f" ")
                self.longitude2.configure(text=f" ")
                
                ''' VELOCITY GRAPHING '''
                if self.prev_speed_time is None: # Compute vertical speed using the change in Relative_Altitude over time.
                    self.prev_speed_time = t_now
                    self.prev_altitude_for_speed = Relative_Altitude
                    current_vertical_speed = 0
                else:
                    dt_speed = t_now - self.prev_speed_time
                    current_vertical_speed = ((Relative_Altitude - self.prev_altitude_for_speed) / dt_speed) if dt_speed > 0 else 0
                    self.prev_speed_time = t_now
                    self.prev_altitude_for_speed = Relative_Altitude

                # Update the horizontal and vertical speed data deques.
                self.horiz_speed_time.append(current_time)
                self.horiz_speed_data.append(computed_horiz_speed)
                self.vert_speed_time.append(current_time)
                self.vert_speed_data.append(current_vertical_speed)

                # Update the line data for the graph.
                self.line_horiz_speed.set_data(self.horiz_speed_time, self.horiz_speed_data)
                self.line_vert_speed.set_data(self.vert_speed_time, self.vert_speed_data)

                # Adjust the x-axis limits based on current time data.
                if len(self.horiz_speed_time) > 1:
                    t_min = min(self.horiz_speed_time)
                    t_max = max(self.horiz_speed_time)
                    
                    self.ax_speed_hori.set_xlim(t_min, t_max if t_min != t_max else (t_min - 10, t_max + 10))
                    self.ax_speed_vert.set_xlim(t_min, t_max if t_min != t_max else (t_min - 10, t_max + 10))

                self.ax_speed_hori.relim()
                self.ax_speed_vert.relim()
                self.ax_speed_hori.autoscale_view()
                self.ax_speed_vert.autoscale_view()
                self.canvas_speed_hori.draw()
                self.canvas_speed_vert.draw()
                
                ''' GPS CORRDINATES UPDATES '''
                self.map_widget.set_position(Latitude, Longitude)
                self.map_marker.set_position(Latitude, Longitude)
                
                ''' PRESSURE AND RELATIVE ALTITUDE GRAPHING '''
                self.alt_time_history.append(current_time)
                self.alt_data_history.append(Relative_Altitude)
                self.alt_line.set_data(self.alt_time_history, self.alt_data_history)
                
                if len(self.alt_time_history) > 1:
                    x_min = min(self.alt_time_history)
                    x_max = max(self.alt_time_history)
                    self.ax_alt.set_xlim(x_min, x_max if x_min != x_max else (x_min - 10, x_max + 10))
                self.ax_alt.relim()
                self.ax_alt.autoscale_view()
                self.canvas_alt.draw()

                self.press_time_history.append(current_time)
                self.press_data_history.append(Pressure)
                self.press_line.set_data(self.press_time_history, self.press_data_history)
                
                if len(self.press_time_history) > 1:
                    x_min = min(self.press_time_history)
                    x_max = max(self.press_time_history)
                    self.ax_press.set_xlim(x_min, x_max if x_min != x_max else (x_min - 10, x_max + 10))
                self.ax_press.relim()
                self.ax_press.autoscale_view()
                self.canvas_press.draw()
                
                ''' ABSOLUTE AND RELATIVE ALTITUDE STATUS '''
                if ser is None or not ser.is_open:
                    status_abs_alt       = "NDA"
                    status_rel_alt       = "NDA"
                    status_latency       = "STANDING BY"
                    status_abs_alt_color = "orange"
                    status_rel_alt_color = "orange"
                    status_latency_color = "orange"
                else:
                    status_abs_alt       = f"{Absolute_Altitude:.4f} m"
                    status_rel_alt       = f"{Relative_Altitude:.4f} m"
                    status_latency       = f"{latency:.4f} ms"
                    status_abs_alt_color = "white"
                    status_rel_alt_color = "white"
                    status_latency_color = "white"
                self.absolute_label.configure(text=status_abs_alt, text_color=status_abs_alt_color)
                self.relative_label.configure(text=status_rel_alt, text_color=status_rel_alt_color)
                self.latency_label.configure(text=status_latency, text_color=status_latency_color)
                
                ''' FLIGHT PATH CALCULATION ENGINE '''
                if self.ref_lat is None and Latitude != 0 and Longitude != 0:
                    self.ref_lat = Latitude
                    self.ref_lon = Longitude
                if self.ref_lat is not None:
                    x_local, y_local = latlon_to_local_xy(Latitude, Longitude, self.ref_lat, self.ref_lon)
                    self.x_data.append(x_local)
                    self.y_data.append(y_local)
                    self.z_data.append(Relative_Altitude)
                
                    if self.prev_alt_time is None:
                        self.prev_alt_time = t_now
                        self.prev_altitude = Relative_Altitude
                        vertical_speed     = 0
                    else:
                        dt_alt             = t_now - self.prev_alt_time
                        vertical_speed     = (Relative_Altitude - self.prev_altitude) / dt_alt if dt_alt > 0 else 0
                        self.prev_alt_time = t_now
                        self.prev_altitude = Relative_Altitude
                
                    self.ax_flight.cla()
                    self.ax_flight.set_title("CanSat Flight Path")
                    self.ax_flight.set_xlabel("East/West (m)")
                    self.ax_flight.set_ylabel("North/South (m)")
                    self.ax_flight.set_zlabel("Altitude (m)")
                
                    if len(self.x_data) > 1:
                        self.ax_flight.plot(list(self.x_data), list(self.y_data), list(self.z_data), color='green', label='Flight Path')
                    self.ax_flight.scatter([self.x_data[-1]], [self.y_data[-1]], [self.z_data[-1]], color='red', marker='o', label='Current')
                
                    if vertical_speed < 0 and Relative_Altitude > 0 and len(self.x_data) >= 2:
                        time_to_land = Relative_Altitude / abs(vertical_speed)
                        dx   = self.x_data[-1] - self.x_data[-2]
                        dy   = self.y_data[-1] - self.y_data[-2]
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist > 0:
                            vx          = computed_horiz_speed * (dx / dist)
                            vy          = computed_horiz_speed * (dy / dist)
                            predicted_x = self.x_data[-1] + vx * time_to_land
                            predicted_y = self.y_data[-1] + vy * time_to_land
                            self.ax_flight.scatter([predicted_x], [predicted_y], [0], color='red', marker='x', label='Predicted Landing')
                            
                            # Convert the predicted local coordinates back to lat/lon using the reference
                            pred_lat, pred_lon = local_to_latlon(predicted_x, predicted_y, self.ref_lat, self.ref_lon)
                            self.predicted_lat = pred_lat
                            self.predicted_lon = pred_lon
                            Latitude_Pred      = pred_lat
                            Longitude_Pred     = pred_lon
                            
                            self.latitude_predict.configure(text=f"Latitude:   {pred_lat:.8f}")
                            self.longitude_predict.configure(text=f"Longitude: {pred_lon:.8f}")
                            self.map_widget_pred.set_position(Latitude_Pred, Longitude_Pred)
                            self.map_marker_pred.set_position(Latitude_Pred, Longitude_Pred)

                    self.ax_flight.legend()
                    self.canvas_flight.draw()
                    
                current_time_latency = time.time()
                if last_data_timestamp > 0:
                    latency = (current_time_latency - last_data_timestamp) * 1000
                    
            if ser is None or not ser.is_open:
                comport_status       = "COM Port:"
                baud_status          = "Baud Rate:"
                comport_status_color = "orange"
                baud_status_color    = "orange"
            else:
                comport_status       = "COM Port:"
                baud_status          = "Baud Rate:"
                comport_status_color = "green"
                baud_status_color    = "green"
            self.com_port_label.configure(text=comport_status, text_color=comport_status_color)
            self.baud_rate_label.configure(text=baud_status, text_color=baud_status_color)
                    
            ''' SYSTEM USAGE AND INPUT LATENCY UTILITY '''
            cpu_usage = psutil.cpu_percent(interval=None)

            # Memory usage (percentage)
            mem = psutil.virtual_memory()
            mem_usage = mem.percent

            # GPU usage (percentage) if GPUtil is installed and GPU is available
            gpu_usage = 0
            if GPUtil:
                gpus = GPUtil.getGPUs()
                if gpus:
                    # For simplicity, use the first GPU
                    gpu_usage = gpus[0].load * 100
            
            self.cpu_usage.configure(text=f"CPU Usage: {cpu_usage}%")
            self.gpu_usage.configure(text=f"GPU Usage: {gpu_usage:.1f}%")
            self.ram_usage.configure(text=f"Memory Usage: {mem_usage}%")
                    
        except Exception as e:
            print("UI update error:", e)
            #messagebox.showerror("Error", f"An error occurred while updating the UI: {e}")
        
        self.main_window.after(20, self.update_ui) # Dictates the cycle speed of the update

    def run(self):
        self.main_window.mainloop()
        
    # ---------------------------
    # New Button Callback Methods
    # ---------------------------
    def toggle_save_data(self):
        try:
            # Read the data from the serial port using your existing function.
            data = read_com_data(ser)
            if data is None:
                print("No data received from COM port.")
                return
            
            # Define the columns in the desired order.
            columns = [
                "Pressure", "Relative_Altitude", "MS5611_Temperature", "Thermistor",
                "Latitude", "Longitude", "SD_Card_Status", "Time_Elapsed",
                "BNO08x_Status", "Yaw", "Pitch", "Roll", "Velocity", "Absolute_Altitude"
            ]
            
            # Format the data as a comma-separated line.
            line = ",".join(str(data[col]) for col in columns)
            
            # Append the line to a text file.
            with open("serial_data_log.txt", "a") as f:
                f.write(line + "\n")
                
            print("Data saved:", line)
            
        except Exception as e:
            print("Error saving serial data:", e)

    def toggle_buzzer(self):
        messagebox.showinfo("FEATURE UNAVAILABLE", "TOGGLE BUZZER FEATURE COMING SOON!")
        #if hasattr(self, 'buzzer_on') and self.buzzer_on:
        #    command_queue.put("BZ0")
        #    self.buzzer_on = False
        #else:
        #    command_queue.put("BZ1")
        #    self.buzzer_on = True

    def erase_saved_data(self):
        messagebox.showinfo("FEATURE UNAVAILABLE", "REMOTE MANUAL DATA RESET FEATURE COMING SOON!")
        #command_queue.put("ERD")

    def reboot_device(self):
        messagebox.showinfo("FEATURE UNAVAILABLE", "REBOOT FEATURE COMING SOON!")
        #command_queue.put("REBOOT")

    def start_receiving_data(self):
        global running, ser, current_port
        # If already running, warn and return.
        if running:
            messagebox.showwarning("CONNECTION ALREADY ESTABLISHED", 
                                f"Already connected to the port: {current_port}")
            return

        try:
            running = True
            self.receiving_data = True
            ser = None  # Reset serial object before starting
            
            # Create and store the thread object.
            self.serial_thread_obj = Thread(target=serial_thread, daemon=True)
            self.serial_thread_obj.start()
            
            # Optionally, send a command to start data reception.
            # command_queue.put("STXD")
        except Exception as e:
            messagebox.showerror("CONNECTION ERROR", f"Error starting serial port: {e}")


    def stop_receiving_data(self):
        global running, ser, current_port
        # Check if there's an active connection
        if ser is None or not ser.is_open:
            messagebox.showerror("CONNECTION PROBLEM", "You are not connected to any devices.")
            return

        try:
            running = False  # Signal the serial thread to exit its loop
            
            # If the serial thread was stored, join it to wait for its termination.
            if hasattr(self, 'serial_thread_obj'):
                self.serial_thread_obj.join(timeout=1)
            
            current_port = None
            ser.close()  # Since ser is open (from our check), close it.
            self.receiving_data = False
        except Exception as e:
            messagebox.showerror("CONNECTION ERROR", f"Error stopping serial port: {e}")

    def choose_com_port(self, port_name):
        global COM_PORT
        COM_PORT = port_name
        #print(f"Selected COM Port: {COM_PORT}")
        
    def choose_baud_rate(self, baud_rate):
        global BAUD_RATE
        BAUD_RATE = baud_rate
        #print(f"Selected Baud Rate: {BAUD_RATE}")

    def update_com_ports(self):
        available_ports = get_available_com_ports()
        self.com_port_option.configure(values=available_ports)
        global COM_PORT
        if COM_PORT not in available_ports and available_ports:
            self.com_port_option.set(available_ports[0])
            self.choose_com_port(available_ports[0])
        self.main_window.after(5000, self.update_com_ports)
        
    # ---------------------------
    # Existing Methods (Callbacks for logout, exit, etc.)
    # ---------------------------
    def system_check(self):
        messagebox.showinfo("SYSTEM CHECK", "Running system check, see console window for details.")

    def logout(self):
        global running, ser, current_port
        if messagebox.askyesno("LOGOUT OF SESSION", "Are you sure you want to logout?"):
            running = False  # Signal the serial thread to exit its loop

            # If the serial thread was stored, join it to wait for its termination.
            if hasattr(self, 'serial_thread_obj'):
                self.serial_thread_obj.join(timeout=1)

            current_port = None
            if ser is not None and ser.is_open:
                ser.close()
            self.receiving_data = False
            time.sleep(1)
            self.main_window.destroy()
            runpy.run_path("login.py", run_name="__main__")
            # Alternatively, if you prefer:
            # import login
            # login.start_program()

    def exit_app(self):
        if messagebox.askyesno("EXIT APPLICATION", "Are you sure you want to exit?"):
            self.main_window.destroy()

if __name__ == "__main__":
    app = TelemetryDashboard()
    app.run()
    
'''    
pr.disable()
s = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
'''