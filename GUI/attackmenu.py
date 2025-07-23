import customtkinter as ctk
from PIL import Image
from noti import show_toast

class AttackMenu(ctk.CTkFrame):
    def __init__(self, master, on_back=None):
        super().__init__(master, fg_color="transparent")
        self.on_back = on_back

        # Logo
        try:
            logo_img = ctk.CTkImage(light_image=Image.open("logo.png"), size=(60, 60))
            logo_button = ctk.CTkButton(master=self, image=logo_img, text="", width=70, height=70, command=self.logo_pressed)
        except:
            logo_button = ctk.CTkButton(master=self, text="HonkLab", font=("Arial", 14), command=self.logo_pressed, width=100, height=40)
        logo_button.place(x=10, y=10)

        # Title
        title_label = ctk.CTkLabel(master=self, text="Attack Menu", font=("Arial", 20, "bold"))
        title_label.place(x=180, y=20)

        # Attack Options
        ctk.CTkButton(self, text="▶ Replay", command=self.replay_attack, width=120, height=40).place(x=180, y=80)
        ctk.CTkButton(self, text="📡 Relay", command=self.relay_attack, width=120, height=40).place(x=180, y=130)
        ctk.CTkButton(self, text="🔁 RollJam", command=self.rolljam_attack, width=120, height=40).place(x=180, y=180)

        # Back Button
        ctk.CTkButton(self, text="◀ Back", command=self.go_back, width=80, height=30).place(x=10, y=270)

    def logo_pressed(self):
        show_toast(self, "Logo", type="info")

    def replay_attack(self):
        show_toast(self, "Opening Replay GUI", type="info")
        self.master.show_replay_menu()

    def relay_attack(self):
        show_toast(self, "Relay GUI WIP", type="warning")

    def rolljam_attack(self):
        show_toast(self, "RollJam GUI WIP", type="warning")

    def go_back(self):
        if self.on_back:
            self.on_back()



