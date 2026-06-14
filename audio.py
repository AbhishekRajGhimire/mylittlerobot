import winsound
import os

class AudioSystem:
    def __init__(self):
        self.enabled = True

    def play_sound(self, sound_name):
        if not self.enabled:
            return
        path = os.path.join('assets', f'{sound_name}.wav')
        if os.path.exists(path):
            winsound.PlaySound(path, winsound.SND_ASYNC | winsound.SND_FILENAME)

    def toggle(self):
        self.enabled = not self.enabled
