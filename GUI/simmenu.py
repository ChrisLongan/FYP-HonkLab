import customtkinter as ctk
from PIL import Image
import subprocess

class SimulationTab(ctk.CTkFrame):
    def __init__(self, master, on_back=None):
        super().__init__(master)
        self.on_back = on_back
        self.configure(fg_color="#1E1E1E")

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="--RF Simulation Toolkit--",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        # Dropdown
        self.simulation_option = ctk.CTkOptionMenu(
            self, values=["Signal Viewer", "Attack Flow"],
            command=self.switch_simulation
        )
        self.simulation_option.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="w")

        # Simulation Content
        self.simulation_frame = ctk.CTkFrame(self, fg_color="#2A2A2A")
        self.simulation_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.simulation_frame.grid_columnconfigure(0, weight=1)
        self.simulation_frame.grid_rowconfigure(0, weight=1)

        # Back Button
        if self.on_back:
            back_btn = ctk.CTkButton(self, text="⬅ Back", command=self.on_back)
            back_btn.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="w")

        # Load default
        self.switch_simulation("Signal Viewer")

    def switch_simulation(self, choice):
        for widget in self.simulation_frame.winfo_children():
            widget.destroy()

        if choice == "Signal Viewer":
            label = ctk.CTkLabel(
                self.simulation_frame, text="📡 View Live Spectrum",
                font=ctk.CTkFont(size=16)
            )
            label.pack(pady=10)

            view_btn = ctk.CTkButton(
                self.simulation_frame, text="Launch Signal Viewer",
                command=self.launch_signal_viewer
            )
            view_btn.pack(pady=20)

        elif choice == "Attack Flow":
            ctk.CTkLabel(
                self.simulation_frame, text="🎓 Attack Flow Simulator",
                font=ctk.CTkFont(size=16)
            ).pack(pady=10)

            ctk.CTkLabel(
                self.simulation_frame,
                text="[Flow animation or educational diagram will appear here soon]",
                wraplength=400
            ).pack(pady=20)

    def launch_signal_viewer(self):
        try:
            subprocess.Popen(["python3", "/home/pi/FYP-HonkLab/SimulationMode/signalcap.py"])
        except Exception as e:
            print(f"[ERROR] Failed to launch viewer: {e}")
