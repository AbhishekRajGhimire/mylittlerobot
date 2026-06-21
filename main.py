import sys
import os
from PyQt6.QtWidgets import QApplication
from pet_window import DesktopPet
from updater import start_updater

APP_VERSION = "v1.1.0"

def cleanup_old_updates():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        old_exe_path = os.path.join(exe_dir, "MyLittleRobot.old.exe")
        update_exe_path = os.path.join(exe_dir, "MyLittleRobot_update.exe")
        
        for path in [old_exe_path, update_exe_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Cleanup failed for {path}: {e}")

if __name__ == '__main__':
    cleanup_old_updates()
    start_updater(APP_VERSION)
    
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())
