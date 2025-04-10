from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPlainTextEdit,
    QPushButton, QComboBox, QSizePolicy
)
from PyQt5.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Thermal Plate Simulation")


        # === Layouts ===
        self.main_layout = QVBoxLayout(self)
        self.second_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Import dropdown
        self.cb_import = QComboBox()
        self.cb_import.currentIndexChanged.connect(self.controller.load_params)
        self.main_layout.addWidget(self.cb_import)

        # Grid for inputs
        grid = QGridLayout()
        self.main_layout.addLayout(grid)

        def add_input(label, row, attr_name, placeholder=""):
            label_widget = QLabel(label)
            field = QPlainTextEdit()
            field.setMaximumHeight(28)
            field.setPlaceholderText(placeholder)
            field.textChanged.connect(self.controller.autosave)
            setattr(self, attr_name, field)
            grid.addWidget(label_widget, row, 0)
            grid.addWidget(field, row, 1)

        # === Input Fields ===
        add_input("Total Time [s]:", 0, "zone_total_time", "500")
        add_input("Length Y [mm]:", 1, "zone_length", "61")
        add_input("Length X [mm]:", 2, "zone_Depth", "116")
        add_input("Thickness [mm]:", 3, "zone_thick", "1.8")
        add_input("N:", 4, "zone_n", "117")
        add_input("Thermal Conductivity [W/mK]:", 5, "zone_k", "350")
        add_input("Density [kg/m3]:", 6, "zone_rho", "2333")
        add_input("Heat Capacity [J/kgK]:", 7, "zone_cp", "896")
        add_input("Convection Coeff [W/m2K]:", 8, "zone_h", "13.5")
        add_input("Amperage Input [A]:", 9, "zone_amp_in", "-1.0")
        add_input("Power transfert [W/A] :", 10, "zone_power_transfert", "-1.0")
        add_input("Ambient Temp [°C]:", 11, "zone_ambient_temp", "23.8")
        add_input("Initial Temp [°C]:", 12, "zone_initial_temp", "0")
        add_input("Position heat source [(X, Y)]:", 13, "zone_position_heat_source", "(X, Y)")
        add_input("Position thermistance 1 [(X, Y)]:", 14, "zone_positions_thermistance_1", "(X, Y)")
        add_input("Position thermistance 2 [(X, Y)]:", 15, "zone_positions_thermistance_2", "(X, Y)")
        add_input("Position thermistance 3 [(X, Y)]:", 16, "zone_positions_thermistance_3", "(X, Y)")
        add_input("Start heat time [s]:", 17, "zone_start_heat_time", "-1.0")
        add_input("Stop heat time [s]:", 18, "zone_stop_heat_time", "-1.0")
        add_input("step time [s]:", 19, "zone_step_time", "-1.0")

        # === Save Button ===
        self.save_btn = QPushButton("Save to Json")
        self.save_btn.clicked.connect(self.controller.export_params)
        self.main_layout.addWidget(self.save_btn)

        # === Start Button ===
        self.start_btn = QPushButton("Start Simulation")
        self.start_btn.clicked.connect(self.controller.start_simulation)
        self.main_layout.addWidget(self.start_btn)

        # === Placeholder ===
        self.sim_canvas_container = QVBoxLayout()
        self.second_layout.addLayout(self.sim_canvas_container)

    def set_secondary_layout(self):
        self.main_layout = self.layout()
        if self.main_layout is not None:
            while self.main_layout.count():
                item = self.main_layout.takeAt(0)
                widget_to_remove = item.widget()
                if widget_to_remove is not None:
                    widget_to_remove.setParent(None)
            
            QWidget().setLayout(self.main_layout)

        self.setLayout(self.second_layout)