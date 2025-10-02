import tkinter as tk

class TkSidePanel:
    """
    A narrow, tall Tk toplevel placed to the right of the game window:
      - red border (outline),
      - 10 buttons stacked vertically,
      - first button is 'GRID' (call the given callback).
    """
    def __init__(self, master, width: int, border_width: int, on_grid_click):
        self.width = int(width)
        self.border_width = int(border_width)
        self.on_grid_click = on_grid_click
        self.arena_on = False

        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)   # clean panel (no title bar)
        self.win.attributes("-topmost", True)
        self.win.withdraw()               # hidden until shown

        # outer frame with red border
        self.outer = tk.Frame(
            self.win,
            bg="red",
            highlightthickness=0,
            bd=self.border_width
        )
        self.outer.pack(fill="both", expand=True)

        # inner area with neutral bg
        self.inner = tk.Frame(self.outer, bg="#1d1d1f")
        self.inner.pack(fill="both", expand=True, padx=1, pady=1)

        # create buttons
        self._build_buttons(self.inner)

        self.visible = False

    def _build_buttons(self, parent):
        # GRID toggle
        self.arena_btn = tk.Button(
            parent,
            text="GRID: OFF",
            height=2,
            command=self._toggle_arena
        )
        self.arena_btn.pack(fill="x", padx=10, pady=6)

        # salvează stilul implicit ca să putem reveni corect pe OFF
        self._arena_default_bg  = self.arena_btn.cget("bg")
        self._arena_default_fg  = self.arena_btn.cget("fg")
        # pe unele platforme `activebackground` poate lipsi; protejăm cu .cget + fallback
        try:
            self._arena_default_activebg = self.arena_btn.cget("activebackground")
        except tk.TclError:
            self._arena_default_activebg = self._arena_default_bg

        # restul butoanelor (placeholders)
        for i in range(2, 11):
            b = tk.Button(parent, text=f"Button {i}", height=2)
            b.pack(fill="x", padx=10, pady=6)

    def _toggle_arena(self):
        self.arena_on = not self.arena_on
        if self.arena_on:
            self.arena_btn.config(
                text="GRID: ON",
                bg="#28a745",
                activebackground="#28a745",
                fg="white"
            )
        else:
            self.arena_btn.config(
                text="GRID: OFF",
                bg=self._arena_default_bg,
                activebackground=self._arena_default_activebg,
                fg=self._arena_default_fg
            )
        if callable(self.on_grid_click):
            self.on_grid_click(self.arena_on)

    def show_at(self, x_left: int, y_top: int, height: int):
        """
        Place the panel at given top-left (global coords) with the given height.
        """
        # geometry string supports signed coords
        self.win.geometry(f"{self.width}x{height}{x_left:+}{y_top:+}")
        if not self.visible:
            self.win.deiconify()
            self.visible = True

    def hide(self):
        if self.visible:
            self.win.withdraw()
            self.visible = False