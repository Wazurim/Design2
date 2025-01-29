from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLabel
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import sys
import app.app_settings_and_ressources as res


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(res.WINDOW_TITLE)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(res.WINDOW_WIDTH, res.WINDOW_HEIGHT)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.__initTitleBar()

        

    def __initTitleBar(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {res.BACKGROUND_COLOR};
                color: {res.FONT_COLOR};
            }}
        """)
        title_bar = QWidget(self)
        title_bar.setGeometry(0, 0, res.WINDOW_WIDTH, 35)
        title_bar.setStyleSheet(f"""
            QWidget {{
                background-color: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:0, 
                stop:0 {res.SECONDARY_COLOR}, stop:1 {res.PRIMARY_COLOR}
            );
            }}
        """)

        ulavallogo_label = QLabel(self)
        ulavallogo_label.setPixmap(QPixmap("app/assets/ulavallogo.png").scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        ulavallogo_label.setGeometry(5, 4, 30, 30)  

        title_bar_label = QLabel(self)
        title_bar_label.setGeometry(45, 0, 1080, 35)
        title_bar_label.setText("Design 2 app")
        title_bar_label.setFont(res.TITLE_BAR_FONT)
        title_bar_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {res.FONT_COLOR};
            }}
        """)

        close_button = QPushButton(self)
        close_button.setGeometry(1035, 0, 45, 35)  
        close_button.setText("X")
        close_button.setFont(res.TITLE_BUTTON_BAR_FONT)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                padding: 5px;
                border-radius: 0px;
                color: {res.FONT_COLOR};
                border: none;
            }}
            QPushButton:hover {{
                background-color: {res.CLOSE_BUTTON_HOVER_COLOR};
            }}
        """)
        close_button.clicked.connect(self.close_window)  
        minimize_button = QPushButton("-", self)
        minimize_button.setGeometry(990, 0, 45, 35)
        minimize_button.setFont(res.TITLE_BUTTON_BAR_FONT)
        minimize_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                padding: 5px;
                border-radius: 0px;
            border: none;
            color: {res.FONT_COLOR};
            }}
            QPushButton:hover {{
                background-color: {res.HOVER_COLOR};
            }}
        """)
        minimize_button.clicked.connect(self.minimize_window)  

        

    def close_window(self):
        self.close()

    def minimize_window(self):
        self.showMinimized()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() <= 35:  
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, "_drag_pos") and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = None