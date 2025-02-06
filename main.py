import sys
from PyQt5.QtWidgets import QApplication
from app.core.app_controller import AppController

def main():
    app = QApplication(sys.argv)
    ac = AppController()
    ac.show_main_window()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 