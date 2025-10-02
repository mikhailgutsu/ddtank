import tkinter as tk

class TkSidePanel:
    """
    A narrow, tall Tk toplevel placed to the right of the game window:
      - red border (outline),
      - 10 buttons stacked vertically,
      - first button is 'ARENA' (call the given callback).
    """
    def __init__(self, master, width: int, border_width: int, on_arena_click):
        self.width = int(width)
        self.border_width = int(border_width)
        self.on_arena_click = on_arena_click

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
        # first button: ARENA (wired)
        btn = tk.Button(parent, text="ARENA", height=2, command=self.on_arena_click)
        btn.pack(fill="x", padx=10, pady=6)

        # nine placeholders, no functionality
        for i in range(2, 11):
            b = tk.Button(parent, text=f"Button {i}", height=2)
            b.pack(fill="x", padx=10, pady=6)

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