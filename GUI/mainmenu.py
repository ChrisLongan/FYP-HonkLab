import customtkinter as ctk
from PIL import Image

class MainMenu(ctk.CTkFrame):
    def __init__(self, master, on_attack_callback=None, on_simulation_callback=None, on_about_callback=None):
        super().__init__(master)
        self.configure(width=480, height=320, fg_color="#1E1E1E")

        self.on_attack_callback = on_attack_callback
        self.on_simulation_callback = on_simulation_callback
        self.on_about_callback = on_about_callback

        try:
            logo_img = ctk.CTkImage(light_image=Image.open("logo.png"), size=(60, 60))
            self.logo_button = ctk.CTkButton(self, image=logo_img, text="", width=70, height=70,
                                             command=self.on_about_callback)
        except:
            self.logo_button = ctk.CTkButton(self, text="HonkLab", font=("Arial", 14), command=self.on_about_callback,
                                             width=100, height=40)
        self.logo_button.place(x=10, y=10)

        self.title_label = ctk.CTkLabel(self, text="Main Menu", font=("Arial", 20, "bold"))
        self.title_label.place(x=180, y=20)

        self.attack_btn = ctk.CTkButton(self, text="⚔ Attack Menu", font=("Arial", 14), width=180, height=40,
                                        command=self.on_attack_callback)
        self.attack_btn.place(x=150, y=100)

        self.simulation_btn = ctk.CTkButton(self, text="🧪 Simulation Menu", font=("Arial", 14), width=180, height=40,
                                            command=self.on_simulation_callback)
        self.simulation_btn.place(x=150, y=160)
