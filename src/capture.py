from Quartz import CGWindowListCreateImage, kCGWindowListOptionIncludingWindow, kCGWindowImageDefault
from Quartz import CoreGraphics as CG
from PIL import Image

def capture_window_image(win_info):
    """
    Capture the given Quartz window info as a PIL.Image (RGBA) or return None.
    """
    if not win_info:
        return None

    b = win_info["kCGWindowBounds"]
    b = win_info.get("kCGWindowBounds", win_info.get(CG.kCGWindowBounds)) or win_info.get(CG.kCGWindowBounds)

    if not b:
        return None

    x, y, w, h = float(b["X"]), float(b["Y"]), float(b["Width"]), float(b["Height"])
    rect = CG.CGRectMake(x, y, w, h)

    wid = win_info.get("kCGWindowNumber", win_info.get(CG.kCGWindowNumber))
    if not wid:
        return None

    cgimg = CGWindowListCreateImage(
        rect,
        kCGWindowListOptionIncludingWindow,
        wid,
        kCGWindowImageDefault,
    )
    if not cgimg:
        return None

    width = int(CG.CGImageGetWidth(cgimg))
    height = int(CG.CGImageGetHeight(cgimg))
    rowbytes = int(CG.CGImageGetBytesPerRow(cgimg))
    provider = CG.CGImageGetDataProvider(cgimg)
    data = CG.CGDataProviderCopyData(provider)
    buf = bytes(data)

    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", rowbytes, 1)
    return img