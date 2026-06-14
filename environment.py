import ctypes
import ctypes.wintypes as wintypes

def get_surface_y(win_id, pet_x, pet_w, pet_y, screen_height):
    user32 = ctypes.windll.user32
    highest_y = screen_height

    def enum_cb(hwnd, lParam):
        nonlocal highest_y
        if hwnd == win_id:
            return True
            
        if user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd):
            ex_style = user32.GetWindowLongW(hwnd, -20)
            if not (ex_style & 0x00000080):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    rect = wintypes.RECT()
                    user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    
                    if rect.left <= pet_x + pet_w // 2 <= rect.right:
                        if rect.top >= pet_y - 15 and rect.top < highest_y:
                            highest_y = rect.top
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    user32.EnumWindows(EnumWindowsProc(enum_cb), 0)
    return highest_y
