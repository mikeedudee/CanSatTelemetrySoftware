import customtkinter
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import pywinstyles
from PIL import Image
import runpy
import sqlite3
import bcrypt

# Path to asset files for this GUI window.
ASSETS_PATH = Path(__file__).resolve().parent / "assets"

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
root = customtkinter.CTk()
root.title("TeresaIV Telemetry Dashboard")
root.iconbitmap(ASSETS_PATH / 'hsd_logo_Fxh_icon.ico')
root.attributes("-fullscreen", True)

def exit_fullscreen(event):
    root.attributes("-fullscreen", False)

root.bind("<Escape>", exit_fullscreen)

def start_program():
    new_root = customtkinter.CTk()
    LoginFrame(new_root)
    new_root.mainloop()

def exit_app(root) -> None:
    if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
        root.destroy()

def open_main_window(root):
    root.destroy()
    #from newui7_stable_rebuild_test_3vpy import TelemetryDashboard  # Ensure file is renamed to newui7_stable.py
    #main_app = TelemetryDashboard()
    #main_app.run()
    runpy.run_path("newui7_stable_rebuild_offlinemap.py", run_name="__main__")
    
class UserDatabase:
    def __init__(self):
        self.conn = sqlite3.connect("cacheInitialization.dll")
        self.create_table()

    def create_table(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print("Database error:", e)
            raise
        
    def verify_user(self, username: str, password: str) -> bool:
        """
        Checks whether the provided username and password match an existing user.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row is None:
                # User not found.
                return False
            stored_hash = row[0]
            # bcrypt.checkpw returns True if the passwords match.
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        except sqlite3.Error as e:
            print("Database error during verification:", e)
            raise


class LoginFrame:
    def __init__(self, root):
        self.root = root
        self.create_login_page()
        
    # Create a login page
    def create_login_page(self):
        global frame, usernameGet, TelemetryLabel, successLabel, buttonExit, nullLabel, Salabel, nullLabel2, versionLabel
        global HsD_Logo, HsD_logoPack, compe_Logo, compe_LogoPack, logoIAUPack, Phillogo, logoSYAE, logoSYAEPack, PhillogoPack
        global passwordGet, error_label, HANGGANGlabel, DULOlabel, copyrightLabel, buttonLogin, versionTeresa, logoIAU
        
        frame = customtkinter.CTkFrame(master=self.root)
        frame.pack(pady=20, padx=60, fill="both", expand=True)
        
        nullLabel      = customtkinter.CTkLabel(master=frame, text="")
        nullLabel2     = customtkinter.CTkLabel(master=frame, text="")
        HANGGANGlabel  = customtkinter.CTkLabel(master=frame, text="HANGGANG", font=("Inter", 100))
        DULOlabel      = customtkinter.CTkLabel(master=frame, text="DULO", font=("Inter", 100))
        Salabel        = customtkinter.CTkLabel(master=frame, text="SA", font=("Inter", 60))
        TelemetryLabel = customtkinter.CTkLabel(master=frame, text="TELEMETRY", font=("Inter", 45))
        usernameGet    = customtkinter.CTkEntry(master=frame, placeholder_text="Username", width=200)
        passwordGet    = customtkinter.CTkEntry(master=frame, placeholder_text="Password", show="*", width=200)
        buttonLogin    = customtkinter.CTkButton(master=frame, text="Login", corner_radius=10, border_color='#141E61', border_width=1, fg_color="#141E61", command=CredentialValidator.login)
        root.bind("<Return>", lambda event: buttonLogin.invoke()) # Bind Enter key to login function
        
        # Use lambda to defer exit_app call until button press
        buttonExit     = customtkinter.CTkButton(master=frame, text="Exit", corner_radius=10, border_color='#141E61', border_width=1, fg_color="#141E61", command=lambda: exit_app(self.root))
        error_label    = customtkinter.CTkLabel(master=frame, text="", font=("Inter", 12), text_color="red")
        successLabel   = customtkinter.CTkLabel(master=frame, text="", font=("Inter", 12), text_color="red")
        copyrightLabel = customtkinter.CTkLabel(master=frame, text="Copyright © 2025 — HANGGANG SA DULO — THIRD YEAR BSAE", font=("Inter", 10))
        versionLabel   = customtkinter.CTkLabel(master=frame, text="buildv 7.8-4 — stable-build", font=("Inter", 10))
        
        # Images — icon
        logoIAU        = customtkinter.CTkImage(light_image=Image.open(ASSETS_PATH / 'IAU Logo.png'), size=(100,100))
        logoIAUPack    = customtkinter.CTkLabel(master=frame, text="", image=logoIAU)
        Phillogo       = customtkinter.CTkImage(light_image=Image.open(ASSETS_PATH / 'Flag_of_the_Philippines.jpg'), size=(250,150))
        PhillogoPack   = customtkinter.CTkLabel(master=frame, text="", image=Phillogo)
        logoSYAE       = customtkinter.CTkImage(light_image=Image.open(ASSETS_PATH / 'syae.png'), size=(105,105))
        logoSYAEPack   = customtkinter.CTkLabel(master=frame, text="", image=logoSYAE)
        HsD_Logo       = customtkinter.CTkImage(light_image=Image.open(ASSETS_PATH / 'HsD Logo.png'), size=(105,105))
        HsD_logoPack   = customtkinter.CTkLabel(master=frame, text="", image=HsD_Logo)
        compe_Logo     = customtkinter.CTkImage(light_image=Image.open(ASSETS_PATH / 'CanSat Compe Logo.png'), size=(105,105))
        compe_LogoPack = customtkinter.CTkLabel(master=frame, text="", image=compe_Logo)
        
        # Pack widgets onto the login page
        self.login_page_packs(frame, nullLabel, nullLabel2, HANGGANGlabel, DULOlabel, Salabel,
                               TelemetryLabel, usernameGet, passwordGet, buttonLogin, buttonExit,
                               error_label, successLabel, copyrightLabel, versionLabel,
                               logoIAUPack, HsD_logoPack, logoSYAEPack, compe_LogoPack, PhillogoPack)
    
    # Packs for Login Page Widgets
    def login_page_packs(self, frame, nullLabel, nullLabel2, HANGGANGlabel, DULOlabel, Salabel,
                         TelemetryLabel, usernameGet, passwordGet, buttonLogin, buttonExit,
                         error_label, successLabel, copyrightLabel, versionLabel,
                         logoIAUPack, HsD_logoPack, logoSYAEPack, compe_LogoPack, PhillogoPack):
        
        nullLabel.grid(row=0, column=0, pady=0, padx=10, sticky='n')
        nullLabel2.grid(row=13, column=0, pady=0, padx=10, sticky='n')
        HANGGANGlabel.grid(row=1, column=0, columnspan=5, pady=0, padx=100, sticky='ne')
        DULOlabel.grid(row=2, column=0, columnspan=5, pady=0, padx=100, sticky='ne')
        Salabel.grid(row=2, column=0, columnspan=5, pady=0, padx=400, sticky='ne')
        TelemetryLabel.grid(row=3, column=0, columnspan=5, pady=0, padx=100, sticky='ne')
        usernameGet.grid(row=3, column=0, columnspan=5, pady=12, padx=100, sticky='w')
        passwordGet.grid(row=4, column=0, columnspan=5, pady=10, padx=100, sticky='w')
        buttonLogin.grid(row=5, column=0, columnspan=5, pady=12, padx=100, sticky='w')
        buttonExit.grid(row=6, column=0, columnspan=5, pady=6, padx=100, sticky='w')
        error_label.grid(row=7, column=0, columnspan=5, pady=10, padx=100, sticky='w')
        successLabel.grid(row=8, column=0, columnspan=5, pady=12, padx=0, sticky='n')
        copyrightLabel.grid(row=9, column=0, columnspan=5, pady=0, padx=0, sticky='n')
        versionLabel.grid(row=11, column=0, columnspan=5, pady=0, padx=10, sticky='n')
        logoIAUPack.grid(row=12, column=1, pady=0, padx=(125,0), sticky='se')
        HsD_logoPack.grid(row=12, column=3, pady=0, padx=10, sticky='sw')
        logoSYAEPack.grid(row=12, column=2, pady=0, padx=10, sticky='se')
        compe_LogoPack.grid(row=12, column=3, pady=0, padx=130, sticky='sw')

        # Widgets Opacity
        pywinstyles.set_opacity(logoIAUPack, value  = 0.8)
        pywinstyles.set_opacity(PhillogoPack, value = 0.8)
        pywinstyles.set_opacity(logoSYAEPack, value = 0.8)
        pywinstyles.set_opacity(HsD_logoPack, value = 0.8)

        frame.grid_columnconfigure((0, 3), weight=1)
        frame.grid_rowconfigure(0, weight=1)

class CredentialValidator:
    global db
    db = UserDatabase()
    
    # Handle login validation
    @staticmethod
    def login() -> None:
        entered_username = usernameGet.get()
        entered_password = passwordGet.get()
        
        if db.verify_user(entered_username, entered_password):
            open_main_window(root)
        else:
            error_label.configure(text="Unrecognized credential.")

if __name__ == "__main__":
    # Launch the login page and start the main event loop
    LoginFrame(root)
    root.mainloop()
