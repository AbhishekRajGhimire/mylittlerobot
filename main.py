import sys
from PyQt6.QtWidgets import QApplication
from pet_window import DesktopPet

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())
