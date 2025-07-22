import customtkinter as ctk
import threading

def show_toast(root, message, duration=2, type="info"):
    def _toast():
        # Color & icon map
        colors = {
            "info":    ("#2E86C1", "ℹ️"),
            "success": ("#27AE60", "✅"),
            "error":   ("#C0392B", "❌"),
            "warning": ("#F39C12", "⚠️")
        }

        bg_color, icon = colors.get(type, ("#34495E", "🔔"))

        # Create toast window
        toast = ctk.CTkToplevel(root)
        toast.overrideredirect(True)             # Removes window frame & controls
        toast.attributes("-topmost", True)       # Stay on top

        # Size and position (top-right of 480x320 screen)
        width, height = 200, 40
        x = root.winfo_screenwidth() - width - 10
        y = 10
        toast.geometry(f"{width}x{height}+{x}+{y}")

        # Frame and label
        frame = ctk.CTkFrame(toast, fg_color=bg_color, corner_radius=10)
        frame.pack(expand=True, fill="both")

        label = ctk.CTkLabel(frame, text=f"{icon} {message}", font=("Arial", 13), text_color="white")
        label.pack(expand=True, padx=8, pady=4)

        # Auto-destroy
        toast.after(duration * 1000, toast.destroy)

    threading.Thread(target=_toast, daemon=True).start()
