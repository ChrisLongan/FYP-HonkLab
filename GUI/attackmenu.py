import customtkinter as ctk
from PIL import Image
from noti import show_toast

class AttackMenu(ctk.CTkFrame):
    def __init__(self, master, on_back=None):
        super().__init__(master)
        self.master = master
        self.on_back = on_back
        self.configure(fg_color="#1E1E1E")

    def replay_attack(self):
        self.master.show_replay_menu() 
        
        try:
            logo_img = ctk.CTkImage(light_image=Image.open("logo.png"), size=(60, 60))
            logo_button = ctk.CTkButton(self, image=logo_img, text="", width=70, height=70, command=self.logo_pressed)
        except:
            logo_button = ctk.CTkButton(self, text="HonkLab", font=("Arial", 14), command=self.logo_pressed)
        logo_button.place(x=10, y=10)

        title_label = ctk.CTkLabel(self, text="Attack Menu", font=("Arial", 20, "bold"))
        title_label.place(x=180, y=20)

        self.replay_button = ctk.CTkButton(self, text="▶ Replay", command=self.master.show_replay_menu, width=120, height=40)
        self.replay_button.place(x=180, y=80)

        self.relay_button = ctk.CTkButton(self, text="📡 Relay", command=self.relay_attack, width=120, height=40)
        self.relay_button.place(x=180, y=130)

        self.rolljam_button = ctk.CTkButton(self, text="🔁 RollJam", command=self.rolljam_attack, width=120, height=40)
        self.rolljam_button.place(x=180, y=180)

        if self.on_back:
            self.back_button = ctk.CTkButton(self, text="⬅ Back", command=self.on_back, width=100)
            self.back_button.place(x=10, y=270)

    def logo_pressed(self):
        show_toast(self, "Logo", type="info")

    def relay_attack(self):
        show_toast(self, "Relay GUI coming soon", type="warning")

    def rolljam_attack(self):
        show_toast(self, "RollJam GUI coming soon", type="warning")



