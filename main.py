import sys
from app.core.app_controller import AppController

def main():
    ac = AppController()
    ac.show_main_window()
    sys.exit(ac.app.exec_())

if __name__ == "__main__":
    main()
