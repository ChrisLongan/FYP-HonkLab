import customtkinter as ctk
import threading

def show_toast(root, message, duration=2, type="info"):
    def _toast():
        # Define color and icon based on type
        colors = {
            "info":    ("#2E86C1", "ℹ️"),
            "success": ("#27AE60", "✅"),
            "error":   ("#C0392B", "❌"),
            "warning": ("#F39C12", "⚠️")
        }

        bg_color, icon = colors.get(type, ("#34495E", "🔔"))

        # Create top-level window with no decorations
        toast = ctk.CTkToplevel(root)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)

        # FIX: Remove resizing/stretching
        toast.geometry("200x40")
        toast.minsize(200, 40)
        toast.maxsize(200, 40)

        # Place at top-right of screen
        x = root.winfo_screenwidth() - 210
        y = 10
        toast.geometry(f"+{x}+{y}")

        # Tight frame and label
        frame = ctk.CTkFrame(toast, fg_color=bg_color, corner_radius=10)
        frame.place(relwidth=1, relheight=1)

        label = ctk.CTkLabel(frame, text=f"{icon} {message}", text_color="white", font=("Arial", 13))
        label.pack(padx=10, pady=4, fill="both", expand=True)

        # Auto-close after duration
        toast.after(duration * 1000, toast.destroy)

    threading.Thread(target=_toast, daemon=True).start()
