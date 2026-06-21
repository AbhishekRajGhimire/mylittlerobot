import ctypes
import ctypes.wintypes as wintypes

def get_surface_y(win_id, pet_x, pet_w, pet_y, screen_height):
    user32 = ctypes.windll.user32
    dwmapi = ctypes.windll.dwmapi
    highest_y = screen_height

    def enum_cb(hwnd, lParam):
        nonlocal highest_y
        if hwnd == win_id:
            return True
            
        if user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd):
            is_cloaked = ctypes.c_int(0)
            dwmapi.DwmGetWindowAttribute(hwnd, 14, ctypes.byref(is_cloaked), ctypes.sizeof(is_cloaked))
            if is_cloaked.value != 0:
                return True
                
            ex_style = user32.GetWindowLongW(hwnd, -20)
            if not (ex_style & 0x00000080) and not (ex_style & 0x00000020):
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
