import tkinter as tk
from PIL import Image
from src.window_finder import find_target_window, window_bounds
from src.overlay import CocoaBorderOverlay
# from src.capture import capture_window_image  # enable if you want the heartbeat image

class SurfTankWatcherApp:
    """
    Tk shell for status + timer; Cocoa overlay draws the red border.
    """
    def __init__(self, target_app: str, poll_ms: int, border_width: int, margin: int):
        self.target_app = target_app
        self.poll_ms = int(poll_ms)

        # Tk UI only for a minimal status panel
        self.root = tk.Tk()
        self.root.title("SurfTank watcher")
        self.root.geometry("420x160")
        self.root.resizable(False, False)

        self.status = tk.Label(self.root, text="Waiting…", font=("Arial", 12))
        self.status.pack(pady=16)

        # Cocoa overlay (transparent, click-through)
        self.overlay = CocoaBorderOverlay(border_width=border_width, margin=margin)

        # Start polling
        self.root.after(0, self._poll_loop)

    def _poll_loop(self):
        """
        Every poll:
          - locate SurfTank window
          - (optional) capture a frame to verify access
          - place/refresh the red border overlay
        """
        try:
            win = find_target_window(self.target_app)
            if not win:
                self.status.config(text=f"{self.target_app} not found ❌", fg="red")
                self.overlay.hide()
            else:
                x, y, w, h = window_bounds(win)

                # Optional: capture for heartbeat (disabled by default)
                # img = capture_window_image(win)
                # if img is None:
                #     self.status.config(
                #         text=f"{self.target_app} found, capture failed ⚠️ (check Screen Recording)",
                #         fg="orange"
                #     )
                #     self.overlay.hide()
                #     self._schedule_next()
                #     return

                self.status.config(
                    text=f"{self.target_app} connected ✅  size: {w}×{h}  pos: {x},{y}",
                    fg="green",
                )
                self.overlay.show_at(x, y, w, h)
        except Exception as e:
            self.status.config(text=f"Error: {e}", fg="red")
            self.overlay.hide()
        finally:
            self._schedule_next()

    def _schedule_next(self):
        self.root.after(self.poll_ms, self._poll_loop)

    def run(self):
        self.root.mainloop()
