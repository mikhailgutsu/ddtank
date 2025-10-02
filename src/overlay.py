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

        self._grid_enabled = False
        self._grid_columns = 10
        self._grid_layers = []  

        self._esp_enabled = False
        self._esp_rect = None     
        self._esp_layers = []      

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
        cols = self._grid_columns
        step = width / cols

        green = NSColor.greenColor().colorWithAlphaComponent_(0.7).CGColor()

        from Quartz import CALayer 
        for i in range(1, cols):
            x = int(round(i * step))
            line = CALayer.layer()
            line.setFrame_(((x, 0), (1, height)))
            line.setBackgroundColor_(green)
            content_layer.addSublayer_(line)
            self._grid_layers.append(line)

    def _clear_esp_layers(self):
        content_layer = self.window.contentView().layer()
        for l in self._esp_layers:
            l.removeFromSuperlayer()
        self._esp_layers = []

    def _rebuild_esp_layers(self):
        self._clear_esp_layers()
        if not (self._esp_enabled and self._esp_rect):
            return
        from Quartz import CALayer
        x, y, w, h = map(int, self._esp_rect)

        white = NSColor.whiteColor().colorWithAlphaComponent_(0.8).CGColor()
        rect = CALayer.layer()
        rect.setFrame_(((x, y), (w, h)))
        rect.setBorderWidth_(1.0)
        rect.setBorderColor_(white)
        rect.setBackgroundColor_(NSColor.clearColor().CGColor())
        self.window.contentView().layer().addSublayer_(rect)
        self._esp_layers.append(rect)

        cols, rows = 20, 12
        line_c = NSColor.whiteColor().colorWithAlphaComponent_(0.25).CGColor()

        step_x = w / cols
        for i in range(1, cols):
            vx = int(round(x + i * step_x))
            v = CALayer.layer()
            v.setFrame_(((vx, y), (1, h)))
            v.setBackgroundColor_(line_c)
            rect.addSublayer_(v)
            self._esp_layers.append(v)

        step_y = h / rows
        for j in range(1, rows):
            hy = int(round(y + j * step_y))
            hline = CALayer.layer()
            hline.setFrame_(((x, hy), (w, 1)))
            hline.setBackgroundColor_(line_c)
            rect.addSublayer_(hline)
            self._esp_layers.append(hline)

    def set_esp(self, enabled: bool, rect_xywh):
        self._esp_enabled = bool(enabled)
        self._esp_rect = rect_xywh
        self._rebuild_esp_layers()

    def set_grid(self, enabled: bool, columns: int = 10):
        self._grid_enabled = bool(enabled)
        self._grid_columns = max(2, int(columns))
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

        H_main = int(CG.CGDisplayBounds(CG.CGMainDisplayID()).size.height)
        ay_top = H_main - oy 

        self.window.setFrameTopLeftPoint_((ox, ay_top))
        self.window.setContentSize_((ow, oh))

        layer = self.window.contentView().layer()
        layer.setBorderWidth_(self.border_width)

        self._rebuild_grid_layers(ow, oh)
        self.window.orderFrontRegardless()

    def hide(self):
        self.window.orderOut_(None)