from replayatk import ReplayGUI
import customtkinter as ctk
from PIL import Image
from noti import show_toast

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("RF Attack Menu")
root.geometry("480x320")
root.resizable(False, False)

# === Frame Container ===
container = ctk.CTkFrame(master=root, width=480, height=320, fg_color="transparent")
container.pack(fill="both", expand=True)

active_frame = None

def show_frame(frame_class):
    global active_frame
    if active_frame:
        active_frame.destroy()
    active_frame = frame_class(container)
    active_frame.pack(fill="both", expand=True)

# === Attack Menu Frame ===
class AttackMenu(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        try:
            logo_img = ctk.CTkImage(light_image=Image.open("logo.png"), size=(60, 60))
            logo_button = ctk.CTkButton(master=self, image=logo_img, text="", width=70, height=70, command=self.logo_pressed)
        except:
            logo_button = ctk.CTkButton(master=self, text="HonkLab", font=("Arial", 14), command=self.logo_pressed, width=100, height=40)
        logo_button.place(x=10, y=10)

        title_label = ctk.CTkLabel(master=self, text="Attack Menu", font=("Arial", 20, "bold"))
        title_label.place(x=180, y=20)

        ctk.CTkButton(self, text="▶ Replay", command=self.replay_attack, width=120, height=40).place(x=180, y=80)
        ctk.CTkButton(self, text="📡 Relay", command=self.relay_attack, width=120, height=40).place(x=180, y=130)
        ctk.CTkButton(self, text="🔁 RollJam", command=self.rolljam_attack, width=120, height=40).place(x=180, y=180)

    def logo_pressed(self):
        show_toast(self, "Logo", type="info")

    def replay_attack(self):
        show_toast(self, "Opening Replay GUI", type="info")
        show_frame(lambda parent: ReplayGUI(parent, on_back_callback=lambda: show_frame(AttackMenu)))

    def relay_attack(self):
        show_toast(self, "Relay GUI coming soon", type="warning")

    def rolljam_attack(self):
        show_toast(self, "RollJam GUI coming soon", type="warning")

# === Start with Attack Menu ===
show_frame(AttackMenu)

root.mainloop()
