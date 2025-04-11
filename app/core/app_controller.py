# app/core/app_controller.py
import numpy as np
from datetime import datetime
import os, sys, ast
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import QTimer

from app.ui.main_window import MainWindow
from app.core.JSON_Handler import JsonHandler
from app.core.plate_transmission import Plate
from app.ui.plate_canvas import PlateCanvas

 

class AppController:
    """Controller object for the app
    """
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(self)
        self.json_handler = JsonHandler()
        self.config_dir = "app/Configs"
        self.canvas = None
        self.working = False
        self.cwd = os.getcwd()
        screen = self.app.primaryScreen()
        available_rect = screen.availableGeometry()

        self.screen_width = int(available_rect.width() * 0.9)
        self.screen_height = int(available_rect.height() * 0.9)
        self.screen_x = available_rect.x() + (available_rect.width() - self.screen_width) // 2
        self.screen_y = available_rect.y() + (available_rect.height() - self.screen_height) // 2
        self.__load_config_list()


    def __load_config_list(self):
        """Load the list of JSON file for the combo box
        """
        if not os.path.exists(self.config_dir):
            print("No config directory found")
            return
        files = [f for f in os.listdir(self.config_dir) if f.endswith(".json")]
        self.main_window.cb_import.addItems(files)
        if "latest.json" in files:
            self.main_window.cb_import.setCurrentText("latest.json")
            self.load_params("latest.json")

    def __update_config_list(self):
        """Update the list of JSON config files in the combo box
        """
        self.main_window.cb_import.currentIndexChanged.disconnect(self.load_params)
        if not os.path.exists(self.config_dir):
            print("No config directory found")
            return
        files = [f for f in os.listdir(self.config_dir) if f.endswith(".json")]
        self.main_window.cb_import.clear()
        self.main_window.cb_import.addItems(files)
        self.main_window.cb_import.currentIndexChanged.connect(self.load_params)


    def show_main_window(self):
        """Display the main window
        """
        self.main_window.setGeometry(self.screen_x, self.screen_y, self.screen_width, self.screen_height)
        self.main_window.show()

    def __show_serial_monitor(self):
        """Show the serial monitor /// DEPRECATED ///
        """
        self.main_window.show()

    def autosave(self):
        """Autosave changes in the altest.json file
        """
        params = self.__fetch_params()
        self.json_handler.write_json_file(os.path.join(self.config_dir, "latest.json"), params)
        self.__update_config_list()

    def __fetch_params(self):
        ui = self.main_window
        return {
            "plate": {
                "Total Time [s]:": ui.zone_total_time.toPlainText(),
                "Length X [mm]:": ui.zone_length.toPlainText(),
                "Length Y [mm]:": ui.zone_Depth.toPlainText(),
                "Thickness [mm]:": ui.zone_thick.toPlainText(),
                "N:": ui.zone_n.toPlainText(),
                "Thermal Conductivity [W/mK]:": ui.zone_k.toPlainText(),
                "Density [kg/m3]:": ui.zone_rho.toPlainText(),
                "Heat Capacity [J/kgK]:": ui.zone_cp.toPlainText(),
                "Convection Coeff [W/m2K]:": ui.zone_h.toPlainText(),
                "Amperage Input [A]:": ui.zone_amp_in.toPlainText(),
                "Power transfert :": ui.zone_power_transfert.toPlainText(),
                "Ambient Temp [°C]:": ui.zone_ambient_temp.toPlainText(),
                "Initial Temp [°C]:": ui.zone_initial_temp.toPlainText(),
                "Position heat source [(X, Y)]:": ui.zone_position_heat_source.toPlainText(),
                "Position thermistance 1 [(X, Y)]:": ui.zone_positions_thermistance_1.toPlainText(),
                "Position thermistance 2 [(X, Y)]:": ui.zone_positions_thermistance_2.toPlainText(),
                "Position thermistance 3 [(X, Y)]:": ui.zone_positions_thermistance_3.toPlainText(),
                "Start heat time [s]:": ui.zone_start_heat_time.toPlainText(),
                "Stop heat time [s]:": ui.zone_stop_heat_time.toPlainText(),
                "step time [s]:": ui.zone_step_time.toPlainText(),
                "Start perturbation time [s]:": ui.zone_start_perturbation_time.toPlainText(),
                "Stop perturbation time [s]:": ui.zone_stop_perturbation_time.toPlainText(),
                "Position perturbation [(X, Y)]:": ui.zone_position_perturbation.toPlainText(),
                "Perturbation [W]:": ui.zone_power_perturbation.toPlainText()
            }
        }

    def load_params(self, filename=None):
        """Load parameters from the specified file

        Args:
            filename (string, optional): Name of the wanted config file. Defaults to None, will leave spaces blank.
        """
        try:
            if filename is None or type(filename) != str:
                filename = self.main_window.cb_import.currentText()

            if not filename.endswith(".json"):
                print(f"[WARN] Ignoring invalid file: {filename}")
                return

            file_path = os.path.join(self.config_dir, filename)
            if not os.path.exists(file_path):
                print(f"[ERROR] File not found: {file_path}")
                return

            if self.json_handler.read_json_file(file_path):
                p = self.json_handler.get_data().get("plate", {})
                ui = self.main_window
                ui.zone_total_time.setPlainText(str(p.get("Total Time [s]:", "")))
                ui.zone_length.setPlainText(str(p.get("Length X [mm]:", "")))
                ui.zone_Depth.setPlainText(str(p.get("Length Y [mm]:", "")))
                ui.zone_thick.setPlainText(str(p.get("Thickness [mm]:", "")))
                ui.zone_n.setPlainText(str(p.get("N:", "")))
                ui.zone_k.setPlainText(str(p.get("Thermal Conductivity [W/mK]:", "")))
                ui.zone_rho.setPlainText(str(p.get("Density [kg/m3]:", "")))
                ui.zone_cp.setPlainText(str(p.get("Heat Capacity [J/kgK]:", "")))
                ui.zone_h.setPlainText(str(p.get("Convection Coeff [W/m2K]:", "")))
                ui.zone_amp_in.setPlainText(str(p.get("Amperage Input [A]:", "")))
                ui.zone_power_transfert.setPlainText(str(p.get("Power transfert :", "")))
                ui.zone_ambient_temp.setPlainText(str(p.get("Ambient Temp [°C]:", "")))
                ui.zone_initial_temp.setPlainText(str(p.get("Initial Temp [°C]:", "")))
                ui.zone_position_heat_source.setPlainText(str(p.get("Position heat source [(X, Y)]:", "")))
                ui.zone_positions_thermistance_1.setPlainText(str(p.get("Position thermistance 1 [(X, Y)]:", "")))
                ui.zone_positions_thermistance_2.setPlainText(str(p.get("Position thermistance 2 [(X, Y)]:", "")))
                ui.zone_positions_thermistance_3.setPlainText(str(p.get("Position thermistance 3 [(X, Y)]:", "")))
                ui.zone_start_heat_time.setPlainText(str(p.get("Start heat time [s]:", "")))
                ui.zone_stop_heat_time.setPlainText(str(p.get("Stop heat time [s]:", "")))
                ui.zone_step_time.setPlainText(str(p.get("step time [s]:", "")))
                ui.zone_start_perturbation_time.setPlainText(str(p.get("Start perturbation time [s]:", "")))
                ui.zone_stop_perturbation_time.setPlainText(str(p.get("Stop perturbation time [s]:", "")))
                ui.zone_position_perturbation.setPlainText(str(p.get("Position perturbation [(X, Y)]:", "")))
                ui.zone_power_perturbation.setPlainText(str(p.get("Perturbation [W]:", "")))

        except Exception as e:
            print(f"[CRITICAL] Failed to load params: {e}")

    def export_params(self):
        """Export the parameters to a JSON file.

        Returns:
            bool: Boolean if the save was a success or fail
        """
        default = os.path.join(self.cwd, self.config_dir)
        file_path, _ = QFileDialog.getSaveFileName(
        None, 
        "Save JSON File",  
        default, 
        "JSON Files (*.json);;All Files (*)"  
        )

        if not file_path:
            QMessageBox.warning(None, "Export Cancelled", "No file selected for export.")
            return False

        try:
            params = self.__fetch_params()
            res = self.json_handler.write_json_file(file_path, params)
            self.__update_config_list()
            return res

        except Exception as e:
            QMessageBox.critical(None, "Export Failed", f"An error occurred while saving:\n{str(e)}")
            return False

    def __verify_param(self):
        """Check if the user entered good values

        Raises:
            Exception: Raise an exception if one criteria is unmatch, will contain the error message for the user to correct

        """
        p = self.__fetch_params()["plate"]
        total_time=float(p["Total Time [s]:"])
        lx=float(p["Length X [mm]:"])
        ly=float(p["Length Y [mm]:"])
        thickness=float(p["Thickness [mm]:"])
        n=int(p["N:"])
        k=float(p["Thermal Conductivity [W/mK]:"])
        rho=float(p["Density [kg/m3]:"])
        cp=float(p["Heat Capacity [J/kgK]:"])
        h_convection=float(p["Convection Coeff [W/m2K]:"])
        amp_in=float(p["Amperage Input [A]:"])
        power_transfer=float(p["Power transfert :"])
        ambient_temp=float(p["Ambient Temp [°C]:"])
        initial_plate_temp=float(p["Initial Temp [°C]:"])
        position_heat_source=ast.literal_eval(p["Position heat source [(X, Y)]:"])
        positions_thermistances=[
            ast.literal_eval(p["Position thermistance 1 [(X, Y)]:"]),
            ast.literal_eval(p["Position thermistance 2 [(X, Y)]:"]),
            ast.literal_eval(p["Position thermistance 3 [(X, Y)]:"])
        ]
        start_heat_time=float(p["Start heat time [s]:"])
        stop_heat_time=float(p["Stop heat time [s]:"])
        start_perturbation=float(p["Start perturbation time [s]:"])
        stop_perturbation=float(p["Stop perturbation time [s]:"])
        position_perturbation=ast.literal_eval(p["Position perturbation [(X, Y)]:"])
        perturbation=float(p["Perturbation [W]:"])

        if total_time < 0:
            raise Exception("Total time must be positive")
        if lx <= 0:
            raise Exception("Length X must be positive")
        if ly <= 0:
            raise Exception("Length Y must be positive")
        if thickness <= 0:
            raise Exception("Thickness must be positive")
        if n < 1:
            raise Exception("N must be greater than or equal to 1")
        if k <= 0:
            raise Exception("Thermal Conductivity must be positive")
        if rho <= 0:
            raise Exception("Density must be positive")
        if cp <= 0:
            raise Exception("Heat Capacity must be positive")
        if h_convection < 0:
            raise Exception("Convection Coeff must be non-negative")
        if ambient_temp < -273.15: 
            raise Exception("Ambient Temp must be greater than or equal to -273.15")
        if initial_plate_temp < -273.15:
            raise Exception("Initial Plate Temp must be greater than or equal to -273.15")
        if position_heat_source[0] < 0 or position_heat_source[0] > lx:
            raise Exception("Position heat source X must be between 0 and Length X")
        if position_heat_source[1] < 0 or position_heat_source[1] > ly:
            raise Exception("Position heat source Y must be between 0 and Length Y")
        for i in range(3):
            if positions_thermistances[i][0] < 0 or positions_thermistances[i][0] > lx:
                raise Exception("Position thermistance X must be between 0 and Length X")
            if positions_thermistances[i][1] < 0 or positions_thermistances[i][1] > ly:
                raise Exception("Position thermistance Y must be between 0 and Length Y")
            
        if position_perturbation[0] < 0 or position_perturbation[0] > lx:
            raise Exception("Position perturbation X must be between 0 and Length X")
        if position_perturbation[1] < 0 or position_perturbation[1] > ly:
            raise Exception("Position perturbation Y must be between 0 and Length Y")
        if start_heat_time < 0 or start_heat_time > total_time:
            raise Exception("Start heat time must be between 0 and Total Time")
        if stop_heat_time < start_heat_time or stop_heat_time > total_time:
            raise Exception("Stop heat time must be between Start Heat Time and Total Time")
        if start_perturbation < 0 or start_perturbation > total_time:
            raise Exception("Start perturbation time must be between 0 and Total Time")
        if stop_perturbation < start_perturbation or stop_perturbation > total_time:
            raise Exception("Stop perturbation time must be between Start Perturbation Time and Total Time")
        if perturbation < 0:
            raise Exception("Perturbation must be positive")
        
        if n > 100:
            reply = QMessageBox.question(
                self.main_window,
                "Maillage élevé ?",
                "Un maillage supérieur à 100 peut entraîner des problèmes de performances. Voulez‑vous procéder ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.No:
                raise Exception("Reduce Meshing!")
                    
        return True

    def start_simulation(self):
        """Start the simulation with the parameters specified in the fields
        """
        
        try:
            self.__verify_param()
            p = self.__fetch_params()["plate"]
            plate = Plate(
                total_time=float(p["Total Time [s]:"]),
                lx=float(p["Length X [mm]:"])/1000,
                ly=float(p["Length Y [mm]:"])/1000,
                thickness=float(p["Thickness [mm]:"])/1000,
                n=int(p["N:"]),
                k=float(p["Thermal Conductivity [W/mK]:"]),
                rho=float(p["Density [kg/m3]:"]),
                cp=float(p["Heat Capacity [J/kgK]:"]),
                h_convection=float(p["Convection Coeff [W/m2K]:"]),
                amp_in=float(p["Amperage Input [A]:"]),
                power_transfer=float(p["Power transfert :"]),
                ambient_temp=float(p["Ambient Temp [°C]:"]),
                initial_plate_temp=float(p["Initial Temp [°C]:"]),
                position_heat_source=ast.literal_eval(p["Position heat source [(X, Y)]:"]),
                positions_thermistances=[
                    ast.literal_eval(p["Position thermistance 1 [(X, Y)]:"]),
                    ast.literal_eval(p["Position thermistance 2 [(X, Y)]:"]),
                    ast.literal_eval(p["Position thermistance 3 [(X, Y)]:"])
                ],
                start_heat_time=float(p["Start heat time [s]:"]),
                stop_heat_time=float(p["Stop heat time [s]:"]),
                start_perturbation=float(p["Start perturbation time [s]:"]),
                stop_perturbation=float(p["Stop perturbation time [s]:"]),
                position_perturbation=ast.literal_eval(p["Position perturbation [(X, Y)]:"]),
                perturbation=float(p["Perturbation [W]:"])
            )
            
            if self.canvas:
                self.main_window.layout().removeWidget(self.canvas)
                self.canvas.setParent(None)
            self.main_window.set_secondary_layout()


            self.canvas = PlateCanvas(controller=self, step_sim_time=float(p["step time [s]:"]))
            self.main_window.layout().addWidget(self.canvas)
            self.canvas.start_simulation(plate)
            self.working = True

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to start simulation:\n{e}")

    def reset_view(self):
        self.canvas.reset_view()

    def stop(self):
        """Stop and save the data to a txt file
        """
        try:
            self.working = False

            times = [x for x in self.canvas.times]
            power = self.canvas.power
            pert = self.canvas.perturbation
            t1 = [x for x in self.canvas.t1]
            t2 = [x for x in self.canvas.t2]
            t3 = [x for x in self.canvas.t3]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_file = os.path.join(os.getcwd(), f"Data/sim_data_{timestamp}.txt")
            np.savetxt(new_file, np.transpose([times, power, pert, t1, t2, t3]))
            
        except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to save data:\n{e}")
                print("times:", times,"power:", power, "perturbation:", pert, "t1:", t1,"t2:", t2, "t3:", t3)

    def quit(self):
        """Stop and save the data to a txt file then quit the app
        """
        self.stop()
        self.app.quit()