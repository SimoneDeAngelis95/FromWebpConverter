import sys
import os

from PyQt6.QtWidgets import QApplication, QStyleFactory
from PyQt6.QtGui import QPalette, QColor
from MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)

    try:
        app.setStyle(QStyleFactory.create('Fusion'))
        light = QPalette()
        # Light palette with subtle grays and red accent
        bg_window = QColor(242, 244, 247)      # #F2F4F7 window background
        bg_base = QColor(255, 255, 255)        # inputs/lists/cards
        bg_alt = QColor(238, 241, 245)         # alternate rows, panels
        bg_button = QColor(233, 238, 243)      # buttons
        text_color = QColor(31, 41, 55)        # #1F2937 primary text
        sub_text = QColor(116, 127, 141)       # muted text
        accent = QColor(211, 47, 47)           # #D32F2F red accent

        light.setColor(QPalette.ColorRole.Window, bg_window)
        light.setColor(QPalette.ColorRole.WindowText, text_color)
        light.setColor(QPalette.ColorRole.Base, bg_base)
        light.setColor(QPalette.ColorRole.AlternateBase, bg_alt)
        light.setColor(QPalette.ColorRole.ToolTipBase, bg_base)
        light.setColor(QPalette.ColorRole.ToolTipText, text_color)
        light.setColor(QPalette.ColorRole.Text, text_color)
        light.setColor(QPalette.ColorRole.Button, bg_button)
        light.setColor(QPalette.ColorRole.ButtonText, text_color)
        light.setColor(QPalette.ColorRole.BrightText, QColor(200, 0, 0))
        light.setColor(QPalette.ColorRole.Link, accent)
        light.setColor(QPalette.ColorRole.Highlight, accent)
        light.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        # Disabled states
        light.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, sub_text)
        light.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, sub_text)
        light.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, sub_text)

        app.setPalette(light)

        app.setStyleSheet(
            """
            QWidget { color: #1F2937; }
            QToolTip { color: #1F2937; background-color: #FFFFFF; border: 1px solid #D0D7E2; }

            /* Buttons */
            QPushButton {
                background-color: #E9EEF3; border: 1px solid #D0D7E2; border-radius: 6px;
                padding: 6px 10px; font-weight: 500; color: #1F2937;
            }
            QPushButton:hover { background-color: #F6F8FA; border-color: #C7D0DB; }
            QPushButton:pressed { background-color: #EDEFF2; }
            QPushButton:disabled { color: #8A8F98; background-color: #EEF1F5; border-color: #D6DEE8; }
            QPushButton:default, QPushButton[accent="true"] {
                border: 1px solid #D32F2F;
            }

            /* Inputs */
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit, QPlainTextEdit {
                background-color: #FFFFFF; border: 1px solid #D0D7E2; border-radius: 6px; padding: 4px 6px;
                selection-background-color: #D32F2F; selection-color: #ffffff; color: #1F2937;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {
                border: 1px solid #D32F2F;
            }
            QComboBox QAbstractItemView {
                background: #FFFFFF; selection-background-color: #D32F2F; selection-color: #ffffff;
                border: 1px solid #D0D7E2; outline: 0; }

            /* Lists */
            QListWidget { background: #FFFFFF; border: 1px solid #D0D7E2; border-radius: 6px; }
            QListWidget::item { padding: 6px; }
            QListWidget::item:selected { background: #D32F2F; color: #ffffff; }
            QListWidget::item:hover { background: #F6F8FA; }

            /* ProgressBar */
            QProgressBar { background: #EEF1F5; border: 1px solid #D0D7E2; border-radius: 6px; text-align: center; }
            QProgressBar::chunk { background: #D32F2F; border-radius: 6px; }

            /* Scrollbars */
            QScrollBar:vertical { background: #EEF1F5; width: 10px; margin: 0; }
            QScrollBar::handle:vertical { background: #D0D7E2; min-height: 20px; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #C7D0DB; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

            QScrollBar:horizontal { background: #EEF1F5; height: 10px; margin: 0; }
            QScrollBar::handle:horizontal { background: #D0D7E2; min-width: 20px; border-radius: 4px; }
            QScrollBar::handle:horizontal:hover { background: #C7D0DB; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

            /* StatusBar */
            QStatusBar { background: #F2F4F7; border-top: 1px solid #D0D7E2; }
            """
        )
    except Exception:
        pass

    # Ensure a default working directory (useful when launched from app bundle)
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        pass

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
