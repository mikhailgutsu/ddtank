# --- configuration constants only ---
TARGET_APP = "SurfTank"   # window owner name substring to search for
POLL_MS = 1000            # capture/poll interval in milliseconds
BORDER_WIDTH = 4          # overlay border thickness (px)
MARGIN = 2                # overlay extra padding around the game window (px)

# side panel sizing and gap
PANEL_WIDTH = 220      # px (narrow & tall)
PANEL_GAP = 12         # px gap between game border and panel

# --- bootstrap app ---
from src.app import SurfTankWatcherApp

if __name__ == "__main__":
    SurfTankWatcherApp(
        target_app=TARGET_APP,
        poll_ms=POLL_MS,
        border_width=BORDER_WIDTH,
        margin=MARGIN,
        panel_width=PANEL_WIDTH,
        panel_gap=PANEL_GAP,
    ).run()