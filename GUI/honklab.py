import customtkinter as ctk
from mainmenu import MainMenu
from replayatk import ReplayGUI 
from attackmenu import AttackMenu  
from simmenu import SimulationTab 

# === Main Application Window ===
class RFToolkitApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HonkLab RF Toolkit")
        self.geometry("480x320")
        self.resizable(False, False)

        # Containers
        self.current_frame = None
        self.show_main_menu()

    def clear_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()

    def show_main_menu(self):
        self.clear_frame()
        self.current_frame = MainMenu(self,
                                      on_attack_callback=self.show_attack_menu,
                                      on_simulation_callback=self.show_simulation_menu,
                                      on_about_callback=self.show_about_info)
        self.current_frame.pack(fill="both", expand=True)

    def show_attack_menu(self):
        self.clear_frame()
        self.current_frame = AttackMenu(self, on_back=self.show_main_menu)
        self.current_frame.pack(fill="both", expand=True)

    def show_replay_menu(self):
        self.clear_frame()
        self.current_frame = ReplayGUI(self, on_back=self.show_main_menu)
        self.current_frame.pack(fill="both", expand=True)

    def show_simulation_menu(self):
        self.clear_frame()
        self.current_frame = SimulationTab(self, on_back=self.show_main_menu)
        self.current_frame.pack(fill="both", expand=True)

    def show_about_info(self):
        ctk.CTkMessagebox(title="About HonkLab",
                          message="HonkLab RF Toolkit\nCreated by ChrisDragon\nAutomotive RF Pentesting Education",
                          icon="info")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = RFToolkitApp()
    app.mainloop()
