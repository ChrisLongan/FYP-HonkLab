import customtkinter as ctk
import threading

def show_toast(root, message, duration=2, type="info", sound=False):
    def _toast():
        # Type → color and icon map
        colors = {
            "info":    ("#2E86C1", "ℹ️"),
            "success": ("#27AE60", "✅"),
            "error":   ("#C0392B", "❌"),
            "warning": ("#F39C12", "⚠️")
        }

        bg_color, icon = colors.get(type, ("#34495E", "🔔"))

        # Toast window
        toast = ctk.CTkToplevel(root)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)

        # Dimensions
        width, height = 200, 40
        x = root.winfo_screenwidth() - width - 10
        y = 10
        toast.geometry(f"{width}x{height}+{x}+{y}")

        # Background color using CTkFrame workaround
        frame = ctk.CTkFrame(toast, fg_color=bg_color, corner_radius=8)
        frame.pack(expand=True, fill="both")

        # Message label
        label = ctk.CTkLabel(
            master=frame,
            text=f"{icon} {message}",
            text_color="white",
            font=("Arial", 13)
        )
        label.pack(expand=True, fill="both", padx=10)

        # Auto-close
        toast.after(duration * 1000, toast.destroy)

    # Run it in a thread to avoid freezing the GUI
    threading.Thread(target=_toast, daemon=True).start()
