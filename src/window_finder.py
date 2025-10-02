from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID,
    kCGWindowOwnerName,
    kCGWindowName,
    kCGWindowBounds,
    kCGWindowNumber,
)

def find_target_window(owner_substring: str):
    """
    Returns (win_info_dict | None).
    Chooses the largest on-screen window whose owner name contains `owner_substring`.
    """
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID) or []
    owner_sub = owner_substring.lower()
    candidates = []
    for w in windows:
        owner = (w.get(kCGWindowOwnerName) or "").strip()
        if owner and owner_sub in owner.lower():
            b = w.get(kCGWindowBounds, {})
            if b and b.get("Width", 0) > 0 and b.get("Height", 0) > 0:
                candidates.append(w)

    if not candidates:
        return None

    best = max(candidates, key=lambda w: w[kCGWindowBounds]["Width"] * w[kCGWindowBounds]["Height"])
    return best

def window_bounds(win_info):
    """
    Returns (x, y, w, h) from win_info (Quartz global top-left coordinates).
    """
    b = win_info[kCGWindowBounds]
    return int(b["X"]), int(b["Y"]), int(b["Width"]), int(b["Height"])

def window_id(win_info):
    """
    Returns the CGWindowID.
    """
    return win_info.get(kCGWindowNumber)