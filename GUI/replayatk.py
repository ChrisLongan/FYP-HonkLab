import customtkinter as ctk
from tkinter import filedialog
import subprocess
import os

class ReplayGUI(ctk.CTkFrame):
    def __init__(self, master, on_back_callback=None):
        super().__init__(master)
        self.on_back_callback = on_back_callback
        self.configure(fg_color="#1E1E1E", width=480, height=320)

        # === Debug label to confirm rendering ===
        self.debug_label = ctk.CTkLabel(self, text="Replay GUI Loaded", font=ctk.CTkFont(size=16, weight="bold"))
        self.debug_label.pack(pady=10)

        # === File Selection ===
        self.file_path = ctk.StringVar()
        browse_btn = ctk.CTkButton(self, text="Browse File", command=self.browse_file)
        browse_btn.pack(pady=5)

        # === Decoder Buttons ===
        decoder_frame = ctk.CTkFrame(self, fg_color="transparent")
        decoder_frame.pack(pady=5)

        ctk.CTkButton(decoder_frame, text="OOK Decode", command=lambda: self.run_decoder("ook")).pack(pady=2)
        ctk.CTkButton(decoder_frame, text="FSK Decode", command=lambda: self.run_decoder("fsk")).pack(pady=2)
        ctk.CTkButton(decoder_frame, text="KeeLoq Brute", command=lambda: self.run_decoder("keeloq")).pack(pady=2)

        # === Output Textbox ===
        self.output_box = ctk.CTkTextbox(self, height=100, font=ctk.CTkFont(size=10))
        self.output_box.pack(padx=10, pady=10, fill="both", expand=True)

        # === Back Button ===
        if self.on_back_callback:
            ctk.CTkButton(self, text="⬅ Back", command=self.on_back_callback).pack(pady=5)

    # def browse_file(self):
    #     path = filedialog.askopenfilename(filetypes=[("Signal Files", "*.txt *.npy")])
    #     if path:
    #         self.file_path.set(path)
    #         self.output_box.insert("end", f"\n✔ File selected: {path}\n")

    # def run_decoder(self, mode):
    #     file = self.file_path.get()
    #     if not file:
    #         self.output_box.insert("end", "\n[ERROR] Please select a signal file first.\n")
    #         return

    #     decoder_scripts = {
    #         "ook": "/home/pi/FYP-HonkLab/AttackMode/decoder_ook.py",
    #         "fsk": "/home/pi/FYP-HonkLab/AttackMode/decoder_fsk.py",
    #         "keeloq": "/home/pi/FYP-HonkLab/AttackMode/decoder_keeloq.py"
    #     }

    #     script_path = decoder_scripts.get(mode)
    #     if not script_path or not os.path.isfile(script_path):
    #         self.output_box.insert("end", f"\n[ERROR] Decoder script not found for mode: {mode}\n")
    #         return

    #     self.output_box.insert("end", f"\n▶ Running {mode.upper()} decoder...\n")
    #     try:
    #         result = subprocess.check_output(["python3", script_path], stderr=subprocess.STDOUT, text=True)
    #         self.output_box.insert("end", result + "\n")
    #     except subprocess.CalledProcessError as e:
    #         self.output_box.insert("end", f"\n[ERROR] Decoder failed:\n{e.output}\n")

