import tkinter as tk
from PIL import Image
from src.window_finder import find_target_window, window_bounds
from src.overlay import CocoaBorderOverlay
from src.side_panel import TkSidePanel
# from src.capture import capture_window_image  # enable if you want the heartbeat image

MINIMAP_RIGHT_PCT = 0.028   # margine dreapta până la marginea mini-hărții
MINIMAP_TOP_PCT   = 0.07   # margine sus până la mini-hartă
MINIMAP_W_PCT     = 0.133   # lățimea mini-hărții
MINIMAP_H_PCT     = 0.155    # înălțimea mini-hărții

class SurfTankWatcherApp:
    """
    Tk shell for status + timer; Cocoa overlay draws the red border.
    """
    def __init__(self, target_app: str, poll_ms: int, border_width: int, margin: int,
                 panel_width: int, panel_gap: int):
        self.target_app = target_app
        self.poll_ms = int(poll_ms)
        self.border_width = int(border_width)
        self.margin = int(margin)
        self.panel_width = int(panel_width)
        self.panel_gap = int(panel_gap)

        self.grid_on = False
        self.esp_on = False

        self.root = tk.Tk()
        self.root.title("SurfTank watcher")
        self.root.geometry("420x160")
        self.root.resizable(False, False)

        self.status = tk.Label(self.root, text="Waitingâ€¦", font=("Arial", 12))
        self.status.pack(pady=16)

        # Cocoa overlay (transparent, click-through) â€” same as before
        self.overlay = CocoaBorderOverlay(border_width=border_width, margin=margin)

        # Side panel with buttons (separate Tk toplevel)
        self.side_panel = TkSidePanel(
            master=self.root,
            width=self.panel_width,
            border_width=self.border_width,
            on_grid_click=self._grid_action,
            on_esp_click=self._esp_action,  # va primi bool
        )

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
                self.status.config(text=f"{self.target_app} not found âŒ", fg="red")
                self.overlay.hide()
                self.side_panel.hide()
            else:
                x, y, w, h = window_bounds(win)
                self.status.config(text=f"{self.target_app} connected ✅  size: {w}×{h}  pos: {x},{y}",
                                   fg="green")
                self.overlay.show_at(x, y, w, h)

                panel_x = x + w + self.margin + self.panel_gap
                panel_y = y
                panel_h = h + 2 * self.margin
                self.side_panel.show_at(panel_x, panel_y, panel_h)

                # GRID redraw
                self.overlay.set_grid(self.grid_on, columns=10)

                # ESP rect (dinamic, în procente)
                if self.esp_on:
                    # calculează rect-ul mini-hărții în coordonate overlay
                    mm_w = int(w * MINIMAP_W_PCT)
                    mm_h = int(h * MINIMAP_H_PCT)
                    mm_right = int(w * MINIMAP_RIGHT_PCT)
                    mm_top = int(h * MINIMAP_TOP_PCT)
                    # colțul stânga-sus al mini-hărții față de fereastra jocului
                    mm_x = (x + w - mm_right - mm_w) - (x - self.margin)  # translatare în overlay
                    mm_y = self.margin + (h - mm_top - mm_h)
                    self.overlay.set_esp(True, (mm_x, mm_y, mm_w, mm_h))
                else:
                    self.overlay.set_esp(False, None)

        except Exception as e:
            self.status.config(text=f"Error: {e}", fg="red")
            self.overlay.hide()
        finally:
            self._schedule_next()

    def _schedule_next(self):
        self.root.after(self.poll_ms, self._poll_loop)

    def run(self):
        self.root.mainloop()

    def _grid_action(self, is_on: bool):
        """Primește True/False de la butonul toggle."""
        self.grid_on = bool(is_on)
        if self.grid_on:
            self.status.config(text="GRID ON: grid 10 coloane activ ✅", fg="blue")
        else:
            self.status.config(text="GRID OFF: grid ascuns ⛔", fg="blue")
        self.overlay.set_grid(self.grid_on, columns=10)

    def _esp_action(self, is_on: bool):
        self.esp_on = bool(is_on)
        if self.esp_on:
            self.status.config(text="ESP ON: mini-hartă marcată ✅", fg="blue")
        else:
            self.status.config(text="ESP OFF: mini-hartă ascunsă ⛔", fg="blue")
            # ascunde layerele ESP când se stinge
            self.overlay.set_esp(False, None)
