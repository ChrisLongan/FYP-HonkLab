import customtkinter as ctk
from PIL import Image

class SimulationTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color=("#1E1E1E"))  

        # === Title ===
        self.title_label = ctk.CTkLabel(
            self,
            text="--RF Simulation Toolkit--",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        # === Simulation Selection Panel ===
        self.simulation_option = ctk.CTkOptionMenu(
            self,
            values=["Signal Viewer", "Attack Flow"],
            command=self.switch_simulation
        )
        self.simulation_option.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="w")

        # === Main Content Area ===
        self.simulation_frame = ctk.CTkFrame(self, fg_color="#2A2A2A")
        self.simulation_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.simulation_frame.grid_columnconfigure(0, weight=1)
        self.simulation_frame.grid_rowconfigure(0, weight=1)

        self.current_sim = None
        self.switch_simulation("Signal Viewer")

    def switch_simulation(self, choice):
        # Clear existing content
        for widget in self.simulation_frame.winfo_children():
            widget.destroy()

        if choice == "Signal Viewer":
            ctk.CTkLabel(self.simulation_frame, text="📊 FFT and Time Domain Viewer Coming Soon...", font=("Arial", 16)).pack(pady=40)

        elif choice == "Attack Flow":
            ctk.CTkLabel(self.simulation_frame, text="🎓 Attack Flow Simulator", font=("Arial", 16)).pack(pady=10)
            ctk.CTkLabel(self.simulation_frame, text="[Flow animation or images will appear here]").pack(pady=20)

    def browse_file(self):
        print("[Browse function placeholder]")