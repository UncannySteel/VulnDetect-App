import sys
import os


# Remove sys.path.append if not needed for imports

from gui.main_gui import MainApp

def main():
    """
    Main entry point: starts the service, API, and GUI.
    """
    app = MainApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()

if __name__ == "__main__":
    main() 