from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPlainTextEdit,
    QPushButton, QComboBox, QSizePolicy, QMessageBox
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
        add_input("Maillage :", 4, "zone_n", "117")
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
        add_input("Start perturbation time [s]:", 20, "zone_start_perturbation_time", "-1.0")
        add_input("Stop perturbation time [s]:", 21, "zone_stop_perturbation_time", "-1.0")
        add_input("Position perturbation [(X, Y)]:", 22, "zone_position_perturbation", "(X, Y)")
        add_input("Perturbation [W]:", 23, "zone_power_perturbation", "-1.0")

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

        self.stop_btn = QPushButton("Stop Simulation")
        self.stop_btn.clicked.connect(self.controller.stop)
        self.second_layout.addWidget(self.stop_btn)

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

    def closeEvent(self, event):
        """
        Called when the user hits the window X or Alt‑F4.
        Save / prompt here, stop worker threads, then accept() or ignore().
        """
        # 1) stop background simulation cleanly
        if getattr(self.controller, "worker", None) and self.controller.worker.isRunning():
            self.controller.worker.stop()
            self.controller.worker.wait()

        # 2) if data changed, prompt the user
        if self.controller.working:        # your own flag / method
            reply = QMessageBox.question(
                self,
                "Quit",
                "Save your work before quitting?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Cancel:
                event.ignore()                # keep the app open
                return
            if reply == QMessageBox.Yes:
                try:
                    self.controller.quit()   # your own save routine
                except Exception as e:
                    QMessageBox.critical(self, "Save failed", str(e))
                    event.ignore()
                    return

        # 3) let Qt proceed with shutdown
        event.accept()