import customtkinter as ctk
import threading

def show_toast(root, message="Processing...", duration=3):
    def toast():
        toast = ctk.CTkToplevel(root)
        toast.overrideredirect(True)  # Remove window decorations
        toast.attributes("-topmost", True)

        # Dimensions
        width, height = 220, 50
        x = root.winfo_screenwidth() - width - 10
        y = 10
        toast.geometry(f"{width}x{height}+{x}+{y}")

        # Message label
        label = ctk.CTkLabel(toast, text=message, font=("Arial", 14))
        label.pack(expand=True, fill="both", padx=10, pady=5)

        # Auto-destroy
        toast.after(duration * 1000, toast.destroy)

    threading.Thread(target=toast, daemon=True).start()
