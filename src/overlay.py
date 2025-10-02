from Quartz import CoreGraphics as CG
from Quartz import CGWindowLevelForKey, kCGOverlayWindowLevelKey
from AppKit import NSWindow, NSApp, NSColor, NSWindowStyleMaskBorderless, NSBackingStoreBuffered

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

        self.window.orderFrontRegardless()

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

        self.window.orderFrontRegardless()

    def hide(self):
        self.window.orderOut_(None)
