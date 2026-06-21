import time
import random
import math
import ctypes
import winreg
import sys
import os
import json
from PyQt6.QtWidgets import QWidget, QMenu, QColorDialog, QApplication
from PyQt6.QtGui import QCursor, QAction, QPainter, QColor
from PyQt6.QtCore import Qt, QTimer, QPoint

def get_running_apps():
    apps = []
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
    import ctypes.wintypes as wintypes
    
    def callback(hwnd, extra):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                apps.append(buff.value.lower())
                
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            process = kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
            if process:
                exe_buff = ctypes.create_unicode_buffer(260)
                if psapi.GetModuleBaseNameW(process, None, exe_buff, 260) > 0:
                    apps.append(exe_buff.value.lower())
                kernel32.CloseHandle(process)
        return True
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    user32.EnumWindows(EnumWindowsProc(callback), 0)
    return apps

from environment import get_surface_y
from physics import PhysicsEngine
from renderer import Renderer
from audio import AudioSystem

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool 
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.resize(120, 150)
        
        self.state = 'falling'
        self.direction = 1 
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        self.screen_geo = QApplication.primaryScreen().availableGeometry()
        self.move(self.screen_geo.width() // 2, 0)
        
        self.anim_time = 0.0
        self.last_cursor_pos = QCursor.pos()
        self.last_cursor_time = time.time()
        self.zzz_particles = []
        
        self.accessory = 'None'
        self.base_color = QColor(80, 120, 160)
        
        self.audio = AudioSystem()
        self.physics = PhysicsEngine()
        
        # New features state
        self.hiding_enabled = True
        self.dancing_enabled = True
        self.load_settings()
        
        self.petting_score = 0
        self.typing_score = 0
        self.last_type_time = time.time()
        self.last_global_mouse_pos = QCursor.pos()
        self.last_global_mouse_time = time.time()
        self.startup_time = time.time()
        self.peek_tilt_multiplier = 1
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_pet)
        self.update_timer.start(30) 
        
        self.behavior_timer = QTimer(self)
        self.behavior_timer.timeout.connect(self.change_behavior)
        self.behavior_timer.start(3000) 
        
        self.dizzy_timer = QTimer(self)
        self.dizzy_timer.timeout.connect(self.recover_from_dizzy)
        self.dizzy_timer.setSingleShot(True)
        
        self.old_pos = None
        self.mouse_history = []
        self.startup_enabled = self.check_startup()

    def get_settings_path(self):
        return os.path.join(os.path.expanduser('~'), '.computerfriend_settings.json')

    def load_settings(self):
        path = self.get_settings_path()
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    settings = json.load(f)
                    
                if 'audio_enabled' in settings:
                    self.audio.enabled = settings['audio_enabled']
                if 'color' in settings:
                    c = settings['color']
                    self.custom_color = QColor(c[0], c[1], c[2])
                if 'accessory' in settings:
                    self.accessory = settings['accessory']
                if 'hiding_enabled' in settings:
                    self.hiding_enabled = settings['hiding_enabled']
                if 'dancing_enabled' in settings:
                    self.dancing_enabled = settings['dancing_enabled']
            except Exception as e:
                print(f"Failed to load settings: {e}")

    def save_settings(self):
        path = self.get_settings_path()
        settings = {
            'audio_enabled': self.audio.enabled,
            'accessory': getattr(self, 'accessory', 'None'),
            'hiding_enabled': getattr(self, 'hiding_enabled', True),
            'dancing_enabled': getattr(self, 'dancing_enabled', True)
        }
        if hasattr(self, 'custom_color'):
            settings['color'] = [self.custom_color.red(), self.custom_color.green(), self.custom_color.blue()]
            
        try:
            with open(path, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def check_startup(self):
        try:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
                
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "MyLittleRobot")
            winreg.CloseKey(key)
            return value == exe_path
        except FileNotFoundError:
            return False

    def toggle_startup_state(self):
        self.startup_enabled = not self.startup_enabled
        try:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
                
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            if self.startup_enabled:
                winreg.SetValueEx(key, "MyLittleRobot", 0, winreg.REG_SZ, exe_path)
            else:
                winreg.DeleteValue(key, "MyLittleRobot")
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Failed to toggle startup: {e}")

    def get_surface_y(self):
        return get_surface_y(int(self.winId()), self.x(), self.width(), self.y() + self.height(), self.screen_geo.height())

    def recover_from_dizzy(self):
        if self.state in ['dizzy', 'funny_face']:
            self.state = 'idle'

    def change_behavior(self):
        apps = get_running_apps()
        has_spotify = any('spotify' in app for app in apps)
        has_video = any('youtube' in app or 'netflix' in app for app in apps)
        
        self.listening_to_music = False

        if self.state in ['dragged', 'thrown', 'falling', 'dizzy', 'funny_face', 'waving', 'sleeping', 'petting', 'working', 'hiding', 'running_to_work', 'watching']:
            if self.state == 'hiding' and random.random() < 0.4:
                self.state = 'idle'
                self.velocity_x = 0
            if self.state == 'watching' and random.random() < 0.2:
                self.state = 'idle'
            return
            
        if has_spotify:
            if self.state == 'dancing':
                if random.random() < 0.9: 
                    return
            elif random.random() < 0.4:
                if self.state != 'dancing':
                    self.dance_anchor_x = float(self.x())
                    self.dance_anchor_y = float(self.y() - 30)
                    self.velocity_x = 0.0
                    self.velocity_y = 0.0
                    
                self.state = 'dancing'
                self.listening_to_music = True
                self.direction = random.choice([-1, 1])
                return
            
        if has_video and random.random() < 0.4:
            self.state = 'watching'
            self.velocity_x = 0
            return
            
        behaviors = ['idle', 'looking_around', 'walking', 'flying', 'following']
        weights = [0.3, 0.2, 0.2, 0.1, 0.2] 
        
        if self.dancing_enabled:
            behaviors.append('dancing')
            weights.append(0.05)
        
        if self.state == 'flying':
            if random.random() < 0.4:
                self.state = 'falling'
            else:
                self.velocity_x = random.choice([-3, 3])
                self.velocity_y = random.choice([-3, -6, 2])
                self.audio.play_sound('woosh')
        else:
            self.state = random.choices(behaviors, weights)[0]
            if self.state in ['idle', 'looking_around']:
                self.velocity_x = 0
            elif self.state == 'walking':
                self.direction = random.choice([-1, 1])
                self.velocity_x = 3.0 * self.direction
            elif self.state == 'following':
                pass 
            elif self.state == 'dancing':
                self.velocity_x = 0
                self.audio.play_sound('dance')
            elif self.state == 'flying':
                self.velocity_y = -15.0 
                self.velocity_x = random.choice([-5, 5])
                self.audio.play_sound('woosh')

    def update_pet(self):
        self.anim_time += 0.1
        self.update() 
        now = time.time()
        
        current_cursor_pos = QCursor.pos()
        
        # Check global mouse speed for hiding
        dt_mouse = max(0.01, now - self.last_global_mouse_time)
        dx_mouse = current_cursor_pos.x() - self.last_global_mouse_pos.x()
        dy_mouse = current_cursor_pos.y() - self.last_global_mouse_pos.y()
        mouse_speed = math.hypot(dx_mouse, dy_mouse) / dt_mouse
        
        pet_center_x = self.x() + self.width() / 2
        pet_center_y = self.y() + self.height() / 2
        dist_to_pet = math.hypot(current_cursor_pos.x() - pet_center_x, current_cursor_pos.y() - pet_center_y)
        
        if self.hiding_enabled and (now - self.startup_time > 3.0) and mouse_speed > 2000 and dist_to_pet < 300 and self.state not in ['dragged', 'thrown', 'falling', 'hiding', 'working', 'petting']:
            self.state = 'hiding'
            self.peek_tilt_multiplier = -1 if random.random() < 0.25 else 1
            
        self.last_global_mouse_pos = current_cursor_pos
        self.last_global_mouse_time = now
        
        # Idle detection
        if current_cursor_pos != self.last_cursor_pos:
            self.last_cursor_pos = current_cursor_pos
            self.last_cursor_time = now
            if self.state in ['waving', 'sleeping', 'dancing']:
                self.state = 'idle'
                self.zzz_particles.clear()
                
        idle_time = now - self.last_cursor_time
        if idle_time > 300:
            if self.state in ['idle', 'looking_around', 'waving']:
                self.state = 'sleeping'
                self.velocity_x = 0
        elif idle_time > 60:
            if self.state in ['idle', 'looking_around']:
                self.state = 'waving'
                self.velocity_x = 0
                self.audio.play_sound('r2d2')

        # Sleeping particles
        if self.state == 'sleeping':
            if random.random() < 0.05:
                self.zzz_particles.append({'x': random.randint(-15, 15), 'y': -60, 'age': 0})
            for z in self.zzz_particles:
                z['y'] -= 0.5
                z['x'] += math.sin(z['age'] * 0.1) * 0.5
                z['age'] += 1
            self.zzz_particles = [z for z in self.zzz_particles if z['age'] < 100]

        # Petting decay
        if self.petting_score > 0:
            self.petting_score -= 2
        if self.state == 'petting' and self.petting_score <= 0:
            self.state = 'idle'
            
        # Keyboard typing polling (using GetAsyncKeyState which checks async key state)
        is_typing = False
        for i in range(8, 190): 
            if ctypes.windll.user32.GetAsyncKeyState(i) & 0x0001:
                is_typing = True
                break
                
        if is_typing:
            self.typing_score += 15
            self.last_type_time = now
        else:
            if self.typing_score > 0:
                self.typing_score -= 1
                
        if self.state not in ['dragged', 'thrown', 'falling', 'hiding', 'petting']:
            if self.typing_score > 100:
                if self.state not in ['working', 'running_to_work']:
                    self.state = 'running_to_work'
            
            if self.state == 'working' and (now - self.last_type_time) > 60:
                self.state = 'waving'
                self.audio.play_sound('r2d2')
                self.typing_score = 0
            elif self.state == 'running_to_work' and (now - self.last_type_time) > 60:
                self.state = 'idle'
                self.typing_score = 0
                
        if self.state == 'dragged':
            return
            
        self.physics.update(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        Renderer.draw(self, painter, QCursor.pos())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            self.state = 'dragged'
            self.mouse_history = [(event.timestamp(), self.pos())]
            self.dizzy_timer.stop()
            self.petting_score = 0

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
            
            self.mouse_history.append((event.timestamp(), self.pos()))
            if len(self.mouse_history) > 10:
                self.mouse_history.pop(0)
        else:
            if self.state not in ['hiding', 'falling', 'thrown', 'working', 'dizzy']:
                self.petting_score += 15
                if self.petting_score > 150:
                    if self.state != 'petting':
                        self.state = 'petting'
                        self.velocity_x = 0
                        self.velocity_y = 0
                        self.audio.play_sound('purr')

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None
            if len(self.mouse_history) >= 2:
                t1, p1 = self.mouse_history[0]
                t2, p2 = self.mouse_history[-1]
                dt = t2 - t1
                if dt > 0:
                    self.velocity_x = ((p2.x() - p1.x()) / dt) * 15.0
                    self.velocity_y = ((p2.y() - p1.y()) / dt) * 15.0
                else:
                    self.velocity_x = 0; self.velocity_y = 0
            else:
                self.velocity_x = 0; self.velocity_y = 0
                
            self.state = 'thrown'

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        color_action = QAction("Change Color", self)
        color_action.triggered.connect(self.change_color)
        menu.addAction(color_action)
        
        reset_color_action = QAction("Reset Default Color", self)
        reset_color_action.triggered.connect(self.reset_color)
        menu.addAction(reset_color_action)
        
        acc_menu = menu.addMenu("Accessories")
        for acc in ['None', 'Top Hat', 'Bow Tie', 'Sunglasses']:
            action = acc_menu.addAction(acc)
            action.setCheckable(True)
            if self.accessory == acc:
                action.setChecked(True)
            action.triggered.connect(lambda checked, a=acc: self.set_accessory(a))
            
        menu.addSeparator()
        
        sound_action = menu.addAction("Sound Enabled")
        sound_action.setCheckable(True)
        sound_action.setChecked(self.audio.enabled)
        sound_action.triggered.connect(self.toggle_audio)
        
        hiding_action = menu.addAction("Enable Peekaboo")
        hiding_action.setCheckable(True)
        hiding_action.setChecked(self.hiding_enabled)
        hiding_action.triggered.connect(self.toggle_hiding)
        
        dancing_action = menu.addAction("Enable Dancing")
        dancing_action.setCheckable(True)
        dancing_action.setChecked(self.dancing_enabled)
        dancing_action.triggered.connect(self.toggle_dancing)
        
        menu.addSeparator()
        
        startup_action = menu.addAction("Run on Startup")
        startup_action.setCheckable(True)
        startup_action.setChecked(self.startup_enabled)
        startup_action.triggered.connect(self.toggle_startup_state)
        
        menu.addSeparator()
        
        quit_action = QAction("Bye bye!", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        menu.exec(event.globalPos())

    def toggle_audio(self):
        self.audio.toggle()
        self.save_settings()

    def change_color(self):
        dialog = QColorDialog()
        dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        if hasattr(self, 'custom_color'):
            dialog.setCurrentColor(self.custom_color)
        else:
            dialog.setCurrentColor(self.base_color)

        accepted = dialog.exec()
        # Tool windows hide on focus loss — force the robot back visible
        self.show()
        self.raise_()

        if accepted:
            color = dialog.selectedColor()
            if color.isValid():
                self.custom_color = color
                self.save_settings()
            
    def reset_color(self):
        if hasattr(self, 'custom_color'):
            delattr(self, 'custom_color')
            self.save_settings()

    def set_accessory(self, acc):
        self.accessory = acc
        self.save_settings()
        
    def toggle_hiding(self):
        self.hiding_enabled = not self.hiding_enabled
        self.save_settings()
        
    def toggle_dancing(self):
        self.dancing_enabled = not self.dancing_enabled
        self.save_settings()
