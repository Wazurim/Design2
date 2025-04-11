from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPlainTextEdit,
    QPushButton, QComboBox, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class MainWindow(QWidget):
    """class for the main window of the application.
 

    Args:
        QWidget (_type_): Widget class from PyQt5
    """
    def __init__(self, controller):
        """_summary_

        Args:
            controller (object AppController): Connector to the app controller
        """
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Simulateur 3D - Plateau de chauffage")
        self.setFont(QFont("Arial", 11))

        # === Layouts ===
        self.main_layout = QVBoxLayout()
        self.second_layout = QVBoxLayout()
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
            label_widget.setFont(QFont("Arial", 11))
            field = QPlainTextEdit()
            field.setMaximumHeight(28)
            
            field.setPlaceholderText(placeholder)
            field.textChanged.connect(self.controller.autosave)
            setattr(self, attr_name, field)
            grid.addWidget(label_widget, row, 0)
            grid.addWidget(field, row, 1)

        # === Input Fields ===
        add_input("Temps de simulation total [s]:", 0, "zone_total_time", "500")
        add_input("Pas de temps [s]:", 1, "zone_step_time", "-1.0")
        add_input("Longueur en X [mm]:", 2, "zone_length", "61")
        add_input("Longueur en Y [mm]:", 3, "zone_Depth", "116")
        add_input("Épaisseur de la plaque [mm]:", 4, "zone_thick", "1.8")
        add_input("Nombre d'éléments au carré (maillage proportionnel X/Y):", 5, "zone_n", "117")
        add_input("Courant d'entrée [A]:", 6, "zone_amp_in", "-1.0")
        add_input("Puissance transférée [W/A]:", 7, "zone_power_transfert", "-1.0")
        add_input("Perturbation [W]:", 8, "zone_power_perturbation", "-1.0")
        add_input("Début du chauffage [s]:", 9, "zone_start_heat_time", "-1.0")
        add_input("Fin du chauffage [s]:", 10, "zone_stop_heat_time", "-1.0")
        add_input("Début de la perturbation [s]:", 11, "zone_start_perturbation_time", "-1.0")
        add_input("Fin de la perturbation [s]:", 12, "zone_stop_perturbation_time", "-1.0")
        add_input("Position de la source de chaleur [(X, Y)]:", 13, "zone_position_heat_source", "(X, Y)")
        add_input("Position de la thermistance 1 [(X, Y)]:", 14, "zone_positions_thermistance_1", "(X, Y)")
        add_input("Position de la thermistance 2 [(X, Y)]:", 15, "zone_positions_thermistance_2", "(X, Y)")
        add_input("Position de la thermistance 3 [(X, Y)]:", 16, "zone_positions_thermistance_3", "(X, Y)")
        add_input("Position de la perturbation [(X, Y)]:", 17, "zone_position_perturbation", "(X, Y)")
        add_input("Température ambiante [°C]:", 18, "zone_ambient_temp", "23.8")
        add_input("Température initiale [°C]:", 19, "zone_initial_temp", "0")
        add_input("Coefficient de convection [W/m²·K]:", 20, "zone_h", "13.5")
        add_input("Conductivité thermique [W/m·K]:", 21, "zone_k", "350")
        add_input("Densité [kg/m³]:", 22, "zone_rho", "2333")
        add_input("Capacité thermique massique [J/kg·K]:", 23, "zone_cp", "896")



        # === Save Button ===
        self.save_btn = QPushButton("Enregister le JSON")
        self.save_btn.clicked.connect(self.controller.export_params)
        self.main_layout.addWidget(self.save_btn)

        # === Start Button ===
        self.start_btn = QPushButton("Démarrer la simulation")
        self.start_btn.clicked.connect(self.controller.start_simulation)
        self.main_layout.addWidget(self.start_btn)

        # === Placeholder ===
        self.sim_canvas_container = QVBoxLayout()
        self.second_layout.addLayout(self.sim_canvas_container)

        # === Save and quit Button ===
        self.stop_btn = QPushButton(" Arreter la simulation et enregistrer les données")
        self.stop_btn.clicked.connect(self.controller.stop)
        self.second_layout.addWidget(self.stop_btn)

        # === reset_view ===
        self.reset = QPushButton(" Reset view orientation")
        self.reset.clicked.connect(self.controller.reset_view)
        self.second_layout.addWidget(self.reset)

    def set_secondary_layout(self):
        """Allows to show the graphs and removes the texts fields #TODO refaire avec des stack layout pour pouvoir revenir au main menu...
        """
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
        """Manage what the app does on windows button close, in this case allows to prevent data loss

        Args:
            event (Windows close event): Windows close event
        """
        if self.controller.working == True:
            reply = QMessageBox.question(
                self,
                "Fermer?",
                "Voulez-vous enregistrer avant de quitter?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Cancel:
                event.ignore()            
                return
            if reply == QMessageBox.Yes:
                try:
                    self.controller.quit()  
                except Exception as e:
                    QMessageBox.critical(self, "Echec de l'enregistrement", str(e))
                    event.ignore()
                    return
        event.accept()