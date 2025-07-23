import customtkinter as ctk
from tkinter import filedialog
import subprocess

class ReplayGUI(ctk.CTkFrame):
    def __init__(self, master, on_back_callback=None):
        super().__init__(master)
        self.on_back_callback = on_back_callback
        self.configure(fg_color="#1E1E1E", width=480, height=320)

        # Title
        ctk.CTkLabel(self, text="Replay Attack", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        # File selection
        self.file_path = ctk.StringVar()
        ctk.CTkButton(self, text="Browse File", font=ctk.CTkFont(size=12), command=self.browse_file).pack(pady=3)

        # Decoder buttons
        ctk.CTkButton(self, text="OOK Decode", font=ctk.CTkFont(size=12),
                      command=lambda: self.run_decoder("ook")).pack(pady=2)

        ctk.CTkButton(self, text="FSK Decode", font=ctk.CTkFont(size=12),
                      command=lambda: self.run_decoder("fsk")).pack(pady=2)

        ctk.CTkButton(self, text="KeeLoq Brute", font=ctk.CTkFont(size=12),
                      command=lambda: self.run_decoder("keeloq")).pack(pady=2)

        # Output box
        self.output_box = ctk.CTkTextbox(self, height=80, font=ctk.CTkFont(size=10))
        self.output_box.pack(pady=5, padx=10, fill="both", expand=True)

        # Back button
        if self.on_back_callback:
            ctk.CTkButton(self, text="⬅ Back", command=self.on_back_callback, font=ctk.CTkFont(size=12)).pack(pady=5)

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("Signal Files", "*.txt *.npy")])
        if path:
            self.file_path.set(path)
            self.output_box.insert("end", f"\n✔ File: {path}\n")

    def run_decoder(self, mode):
        file = self.file_path.get()
        if not file:
            self.output_box.insert("end", "\n[ERROR] No file selected!\n")
            return

        script = {
            "ook": "/home/pi/FYP-HonkLab/AttackMode/decoder_ook.py",
            "fsk": "/home/pi/FYP-HonkLab/AttackMode/decoder_fsk.py",
            "keeloq": "/home/pi/FYP-HonkLab/AttackMode/decoder_keeloq.py"
        }.get(mode)

        if not script:
            self.output_box.insert("end", "\n[ERROR] Invalid decoder mode\n")
            return

        self.output_box.insert("end", f"\n▶ Running {script}...\n")
        try:
            output = subprocess.check_output(["python3", script], stderr=subprocess.STDOUT, text=True)
            self.output_box.insert("end", output + "\n")
        except subprocess.CalledProcessError as e:
            self.output_box.insert("end", f"\n[ERROR]\n{e.output}\n")
