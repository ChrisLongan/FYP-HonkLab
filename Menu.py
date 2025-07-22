import customtkinter as ctk
import tkinter as tk
from PIL import Image
from Notification import show_toast

# Set CustomTkinter theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Set window for 3.5" TFT resolution (landscape)
root = ctk.CTk()
root.title("RF Attack Menu")
root.geometry("480x320")  # TFT resolution
root.resizable(False, False)

# === Callback Functions ===
def logo_pressed():
    show_toast(root, "Logo", type="info")
    print("Logo button pressed")

def replay_attack():
    show_toast(root, "Replay started", type="warning")
    print("Replay Attack triggered")

def relay_attack():
    print("Relay Attack triggered")

def rolljam_attack():
    print("RollJam Attack triggered")

# === UI Layout ===
try:
    logo_img = ctk.CTkImage(light_image=Image.open("logo.png"), size=(60, 60))
    logo_button = ctk.CTkButton(master=root, image=logo_img, text="", width=70, height=70, command=logo_pressed)
except:
    logo_button = ctk.CTkButton(master=root, text="RYGELOCK", font=("Arial", 14), command=logo_pressed, width=100, height=40)

logo_button.place(x=10, y=10)

title_label = ctk.CTkLabel(master=root, text="Attack Menu", font=("Arial", 20, "bold"))
title_label.place(x=180, y=20)

# Attack Buttons - Adjusted for TFT size
replay_btn = ctk.CTkButton(master=root, text="▶ Replay", command=replay_attack, width=120, height=40)
relay_btn = ctk.CTkButton(master=root, text="📡 Relay", command=relay_attack, width=120, height=40)
rolljam_btn = ctk.CTkButton(master=root, text="🔁 RollJam", command=rolljam_attack, width=120, height=40)

replay_btn.place(x=180, y=80)
relay_btn.place(x=180, y=130)
rolljam_btn.place(x=180, y=180)

# Start GUI loop
root.mainloop()
