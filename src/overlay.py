from Quartz import CoreGraphics as CG
from Quartz import CGWindowLevelForKey, kCGOverlayWindowLevelKey
from AppKit import NSWindow, NSColor, NSWindowStyleMaskBorderless, NSBackingStoreBuffered
from AppKit import NSApp

class CocoaBorderOverlay:
    """
    Pure Cocoa overlay window:
      - borderless, clear, always-on-top
      - red CALayer border, no fill
      - click-through (ignores mouse)
      - positioned by top-left (Quartz global coords), margin-aware
    """
    def __init__(self, border_width: int, margin: int):
        self.border_width = int(border_width)
        self.margin = int(margin)

        # Minimal rect; real frame set in show_at()
        rect = CG.CGRectMake(0, 0, 10, 10)
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False
        )
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setIgnoresMouseEvents_(True)
        self.window.setLevel_(CGWindowLevelForKey(kCGOverlayWindowLevelKey))

        content = self.window.contentView()
        content.setWantsLayer_(True)
        layer = content.layer()
        layer.setBackgroundColor_(NSColor.clearColor().CGColor())
        layer.setBorderColor_(NSColor.redColor().CGColor())
        layer.setBorderWidth_(self.border_width)

        # grid state
        self._grid_enabled = False
        self._grid_columns = 10
        self._grid_layers = []  # CASublayers for vertical lines

        self.window.orderFrontRegardless()

    def _clear_grid_layers(self):
        """Remove existing grid line layers."""
        content_layer = self.window.contentView().layer()
        for l in self._grid_layers:
            l.removeFromSuperlayer()
        self._grid_layers = []
    
    def _rebuild_grid_layers(self, width: int, height: int):
        """Create vertical line layers for N equal columns."""
        self._clear_grid_layers()
        if not self._grid_enabled or self._grid_columns < 2:
            return

        content_layer = self.window.contentView().layer()
        # evităm să desenăm pe marginile roșii; grid-ul ocupă tot frame-ul overlay
        # facem N-1 linii verticale
        cols = self._grid_columns
        step = width / cols

        # culoare verde cu ușor alpha
        green = NSColor.greenColor().colorWithAlphaComponent_(0.7).CGColor()

        from Quartz import CALayer  # expus de PyObjC prin Quartz.CoreAnimation
        for i in range(1, cols):
            x = int(round(i * step))
            line = CALayer.layer()
            # 1 px grosime; vertical pe înălțimea ferestrei overlay
            line.setFrame_(((x, 0), (1, height)))
            line.setBackgroundColor_(green)
            content_layer.addSublayer_(line)
            self._grid_layers.append(line)

    def set_grid(self, enabled: bool, columns: int = 10):
        """Public: configurează grid-ul (on/off, nr. coloane)."""
        self._grid_enabled = bool(enabled)
        self._grid_columns = max(2, int(columns))
        # rebuild imediat la dimensiunea curentă
        ow = int(self.window.contentView().frame().size.width)
        oh = int(self.window.contentView().frame().size.height)
        self._rebuild_grid_layers(ow, oh)

    def show_at(self, x: int, y: int, w: int, h: int):
        """
        Place overlay slightly larger than the target window (margin on all sides).
        Input (x, y) are Quartz global top-left coords of the target window.
        """
        ox = int(x - self.margin)
        oy = int(y - self.margin)
        ow = int(w + 2 * self.margin)
        oh = int(h + 2 * self.margin)

        # Convert top-left from Quartz (origin: top-left) to AppKit's expected top-left Y.
        H_main = int(CG.CGDisplayBounds(CG.CGMainDisplayID()).size.height)
        ay_top = H_main - oy  # flipped Y for AppKit top edge

        # Anchor by top-left, then set size
        self.window.setFrameTopLeftPoint_((ox, ay_top))
        self.window.setContentSize_((ow, oh))

        # Keep border width consistent after resize
        layer = self.window.contentView().layer()
        layer.setBorderWidth_(self.border_width)

        # rebuild grid on resize/move
        self._rebuild_grid_layers(ow, oh)
        self.window.orderFrontRegardless()

    def hide(self):
        self.window.orderOut_(None)