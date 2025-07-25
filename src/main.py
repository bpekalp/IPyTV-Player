#!/usr/bin/env python3
"""
IPTV Player Application
Main entry point for the IPTV player application with Xtream Codes support.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt

from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("IPyTV Player")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("IPyTV")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
