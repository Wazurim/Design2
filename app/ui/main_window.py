from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLabel, QPlainTextEdit
from PyQt5.QtGui import QFont, QPixmap, QCursor

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
        self.__initStyleSheet()
        self.__initTitleBar()
        self.__initSimParamZone()

    def __initStyleSheet(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {res.BACKGROUND_COLOR};
                color: {res.FONT_COLOR};
                
            }}

            QLabel {{
                background-color: transparent;
                color: {res.FONT_COLOR};
                }}
            
            QPlainTextEdit {{
                background-color: {res.BACKGROUND_COLOR};    /* dark gray */
                color: {res.FONT_COLOR};               /* near white */
                border: 1px solid {res.PRIMARY_COLOR};
            }}
        """)

    def __initTitleBar(self):

        self.title_bar = QWidget(self)
        self.title_bar.setGeometry(0, 0, res.WINDOW_WIDTH, 35)
        self.title_bar.setStyleSheet(f"""
            QWidget {{
                background-color: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:0, 
                stop:0 {res.SECONDARY_COLOR}, stop:1 {res.PRIMARY_COLOR}
            );
            }}
        """)

        self.ulavallogo_label = QLabel(self)
        self.ulavallogo_label.setPixmap(QPixmap("app/assets/ulavallogo.png").scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.ulavallogo_label.setGeometry(5, 4, 30, 30)  

        self.title_bar_label = QLabel(self)
        self.title_bar_label.setGeometry(45, 0, 1080, 35)
        self.title_bar_label.setText("Design 2 app")
        self.title_bar_label.setFont(res.TITLE_BAR_FONT)
        self.title_bar_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {res.FONT_COLOR};
            }}
        """)

        self.close_button = QPushButton(self)
        self.close_button.setGeometry(1035, 0, 45, 35)  
        self.close_button.setText("X")
        self.close_button.setFont(res.TITLE_BUTTON_BAR_FONT)
        self.close_button.setStyleSheet(f"""
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
        self.close_button.clicked.connect(self.close_window)  
        self.minimize_button = QPushButton("-", self)
        self.minimize_button.setGeometry(990, 0, 45, 35)
        self.minimize_button.setFont(res.TITLE_BUTTON_BAR_FONT)
        self.minimize_button.setStyleSheet(f"""
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
        self.minimize_button.clicked.connect(self.minimize_window)  

    def __initSimParamZone(self):
        
        self.text_total_time = QLabel(self)
        self.text_total_time.setGeometry(20, 50, 250, 32)
        self.text_total_time.setText("TOTAL TIME [s]:")
        self.text_total_time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_total_time.setFont(res.DEFAULT_FONT)
        self.zone_total_time = QPlainTextEdit(self)
        self.zone_total_time.setGeometry(280, 50, 200, 32)
        self.zone_total_time.setPlaceholderText("Total Time")
        self.zone_total_time.setToolTip("Total Time: DESCRIPTION")
        self.zone_total_time.setFont(res.BOLD_FONT)
        self.zone_total_time.setPlainText("500")

        ####
        self.text_lenght = QLabel(self)
        self.text_lenght.setGeometry(20, 100, 250, 32)
        self.text_lenght.setText("LENGHT [m]:")
        self.text_lenght.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_lenght.setFont(res.DEFAULT_FONT)
        self.zone_lenght = QPlainTextEdit(self)
        self.zone_lenght.setGeometry(280, 100, 200, 32)
        self.zone_lenght.setPlaceholderText("Lenght")
        self.zone_lenght.setToolTip("Lenght: DESCRIPTION")
        self.zone_lenght.setFont(res.BOLD_FONT)
        self.zone_lenght.setPlainText("120e-3")

        ####
        self.text_Depth = QLabel(self)
        self.text_Depth.setGeometry(20, 150, 250, 32)
        self.text_Depth.setText("DEPTH [m]:")
        self.text_Depth.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_Depth.setFont(res.DEFAULT_FONT)
        self.zone_Depth = QPlainTextEdit(self)
        self.zone_Depth.setGeometry(280, 150, 200, 32)
        self.zone_Depth.setPlaceholderText("Depth")
        self.zone_Depth.setToolTip("Depth: DESCRIPTION")
        self.zone_Depth.setFont(res.BOLD_FONT)
        self.zone_Depth.setPlainText("120e-3")

        ####
        self.text_thick = QLabel(self)
        self.text_thick.setGeometry(20, 200, 250, 32)
        self.text_thick.setText("THICKNESS [m]:")
        self.text_thick.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_thick.setFont(res.DEFAULT_FONT)
        self.zone_thick = QPlainTextEdit(self)
        self.zone_thick.setGeometry(280, 200, 200, 32)
        self.zone_thick.setPlaceholderText("Thickness")
        self.zone_thick.setToolTip("Thickness: DESCRIPTION")
        self.zone_thick.setFont(res.BOLD_FONT)
        self.zone_thick.setPlainText("1.5e-3")

        ####
        self.text_nx = QLabel(self)
        self.text_nx.setGeometry(20, 250, 250, 32)
        self.text_nx.setText("NUMBER OF ELEMENTS X:")
        self.text_nx.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_nx.setFont(res.DEFAULT_FONT)
        self.zone_nx = QPlainTextEdit(self)
        self.zone_nx.setGeometry(280, 250, 200, 32)
        self.zone_nx.setPlaceholderText("Number of elements x")
        self.zone_nx.setToolTip("Number of elements x: DESCRIPTION")
        self.zone_nx.setFont(res.BOLD_FONT)
        self.zone_nx.setPlainText("120")

        ####
        self.text_ny = QLabel(self)
        self.text_ny.setGeometry(20, 300, 250, 32)
        self.text_ny.setText("NUMBER OF ELEMENTS Y:")
        self.text_ny.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_ny.setFont(res.DEFAULT_FONT)
        self.zone_ny = QPlainTextEdit(self)
        self.zone_ny.setGeometry(280, 300, 200, 32)
        self.zone_ny.setPlaceholderText("Number of elements y")
        self.zone_ny.setToolTip("Number of elements y: DESCRIPTION")
        self.zone_ny.setFont(res.BOLD_FONT)
        self.zone_ny.setPlainText("120")

        
        ####
        self.text_k = QLabel(self)
        self.text_k.setGeometry(10, 350, 260, 32)
        self.text_k.setText("THERMAL CONDUCTIVITY [W/m*k]:")
        self.text_k.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_k.setFont(res.DEFAULT_FONT)
        self.zone_k = QPlainTextEdit(self)
        self.zone_k.setGeometry(280, 350, 200, 32)
        self.zone_k.setPlaceholderText("Thermal Conductivity [W/m*k]")
        self.zone_k.setToolTip("Number of elements y: DESCRIPTION")
        self.zone_k.setFont(res.BOLD_FONT)
        self.zone_k.setPlainText("205")
        
        ####
        self.text_rho = QLabel(self)
        self.text_rho.setGeometry(580, 50, 260, 32)
        self.text_rho.setText("DENSITY [Kg/m^3]:")
        self.text_rho.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_rho.setFont(res.DEFAULT_FONT)
        self.zone_rho = QPlainTextEdit(self)
        self.zone_rho.setGeometry(850, 50, 200, 32)
        self.zone_rho.setPlaceholderText("Density [Kg/m^3]")
        self.zone_rho.setToolTip("Density: DESCRIPTION")
        self.zone_rho.setFont(res.BOLD_FONT)
        self.zone_rho.setPlainText("2700")

        ####
        self.text_cp = QLabel(self)
        self.text_cp.setGeometry(580, 100, 260, 32)
        self.text_cp.setText("HEAT CAPACITY [J/Kg*K]:")
        self.text_cp.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_cp.setFont(res.DEFAULT_FONT)
        self.zone_cp = QPlainTextEdit(self)
        self.zone_cp.setGeometry(850, 100, 200, 32)
        self.zone_cp.setPlaceholderText("Heat capacity [J/Kg*K]")
        self.zone_cp.setToolTip("Heat capacity: DESCRIPTION")
        self.zone_cp.setFont(res.BOLD_FONT)
        self.zone_cp.setPlainText("900")

        ####
        self.text_h = QLabel(self)
        self.text_h.setGeometry(580, 150, 260, 32)
        self.text_h.setText("HEAT TRANSFER [W/m2*K]:")
        self.text_h.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_h.setFont(res.DEFAULT_FONT)
        self.zone_h = QPlainTextEdit(self)
        self.zone_h.setGeometry(850, 150, 200, 32)
        self.zone_h.setPlaceholderText("Heat transfer [W/m2*K]")
        self.zone_h.setToolTip("Heat transfer: DESCRIPTION")
        self.zone_h.setFont(res.BOLD_FONT)
        self.zone_h.setPlainText("20")

        ####
        self.text_power_in = QLabel(self)
        self.text_power_in.setGeometry(580, 200, 260, 32)
        self.text_power_in.setText("POWER INPUT [W]:")
        self.text_power_in.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_power_in.setFont(res.DEFAULT_FONT)
        self.zone_power_in = QPlainTextEdit(self)
        self.zone_power_in.setGeometry(850, 200, 130, 32)
        self.zone_power_in.setPlaceholderText("Power input [W]")
        self.zone_power_in.setToolTip("Power input: DESCRIPTION")
        self.zone_power_in.setFont(res.BOLD_FONT)
        self.zone_power_in.setPlainText("1.5")

        ####
        self.text_ambient_temp = QLabel(self)
        self.text_ambient_temp.setGeometry(580, 250, 260, 32)
        self.text_ambient_temp.setText("AMBIENT TEMP [°C]:")
        self.text_ambient_temp.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_ambient_temp.setFont(res.DEFAULT_FONT)
        self.zone_ambient_temp = QPlainTextEdit(self)
        self.zone_ambient_temp.setGeometry(850, 250, 130, 32)
        self.zone_ambient_temp.setPlaceholderText("Ambient temp [°C]")
        self.zone_ambient_temp.setToolTip("Ambient temp: DESCRIPTION")
        self.zone_ambient_temp.setFont(res.BOLD_FONT)
        self.zone_ambient_temp.setPlainText("20.0")
        
        ####
        self.text_initial_temp = QLabel(self)
        self.text_initial_temp.setGeometry(580, 300, 260, 32)
        self.text_initial_temp.setText("INITIAL TEMP [°C]:")
        self.text_initial_temp.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_initial_temp.setFont(res.DEFAULT_FONT)
        self.zone_initial_temp = QPlainTextEdit(self)
        self.zone_initial_temp.setGeometry(850, 300, 130, 32)
        self.zone_initial_temp.setPlaceholderText("Initial temp [°C]")
        self.zone_initial_temp.setToolTip("Initial temp: DESCRIPTION")
        self.zone_initial_temp.setFont(res.BOLD_FONT)
        self.zone_initial_temp.setPlainText("20.0")

        self.btn_start_simulation = QPushButton("START SIMULATION", self)
        self.btn_start_simulation.setGeometry(700, 420, 180, 60)
        #self.btn_start_simulation.clicked.connect(self.start_simulation)
        self.btn_start_simulation.setFont(res.BOLD_FONT)
        self.btn_start_simulation.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_start_simulation.setFlat(True)
        self.btn_start_simulation.setMouseTracking(True)
        self.btn_start_simulation.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_start_simulation.setToolTip("Start the simulation")
        self.btn_start_simulation.setShortcut("Ctrl+S")



















































#Functions

    def close_window(self):
        self.close()

    def minimize_window(self):
        self.showMinimized()



#Event

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