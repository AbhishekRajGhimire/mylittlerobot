import winsound
import os
import sys

def get_asset_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'assets', filename)
    return os.path.join('assets', filename)

class AudioSystem:
    def __init__(self):
        self.enabled = True
        
    def play_sound(self, sound_name):
        if not self.enabled:
            return
            
        path = get_asset_path(f'{sound_name}.wav')
        if os.path.exists(path):
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        else:
            print(f"Warning: Sound file not found at {path}")

    def toggle(self):
        self.enabled = not self.enabled
