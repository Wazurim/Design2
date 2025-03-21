import os, sys
from app.ui.main_window import MainWindow
from app.core.JSON_Handler import JsonHandler
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from app.core.graph_plate_transmission_copy import Simulateur
from app.ui.Serial_com_gui import SerialMonitor

class AppController:
    def __init__(self):
        self.data = {}
        self.main_window = MainWindow(self)
        self.json_handler = JsonHandler()
        self.cwd = os.getcwd()
        self.config_dir = "app/Configs"
        self.__find_conf()

        self.app = QApplication(sys.argv)
        self.serial_window = SerialMonitor(port="COM9", baudrate=115200)
        screen = self.app.primaryScreen()
        available_rect = screen.availableGeometry()

        width = int(available_rect.width() * 0.8)
        height = int(available_rect.height() * 0.8)
        x = available_rect.x() + (available_rect.width() - width) // 2
        y = available_rect.y() + (available_rect.height() - height) // 2
        self.main_window.setGeometry(x, y, width, height)
        self.serial_window.setGeometry(x, y, width, height)





    def __find_conf(self):
        relative_path = "app/Configs"
        
        absolute_path = os.path.join(self.cwd,relative_path)

        if os.path.exists(absolute_path) and os.path.isdir(absolute_path):
            json_files = [f for f in os.listdir(absolute_path) if f.endswith(".json")]
            self.main_window.cb_import.addItems(json_files)
            if "latest.json" in json_files:
                self.main_window.cb_import.setCurrentIndex(json_files.index("latest.json"))
                self.__load_params("latest.json")
        else:
            print("Config file not found or error while reading config files")

    def __Config_autosave(self):
        data = self.__fetch_params()
        self.json_handler.write_json_file("app/Configs/latest.json", data)

    def __fetch_params(self):
        param = {"plate":{"time" : str(self.main_window.zone_total_time.toPlainText()),
                            "lenght" : str(self.main_window.zone_lenght.toPlainText()),
                            "depth" : str(self.main_window.zone_Depth.toPlainText()),
                            "thickness" : str(self.main_window.zone_thick.toPlainText()),
                            "nx" : str(self.main_window.zone_nx.toPlainText()),
                            "ny" : str(self.main_window.zone_ny.toPlainText()),
                            "k" : str(self.main_window.zone_k.toPlainText()),
                            "rho" : str(self.main_window.zone_rho.toPlainText()),
                            "cp" : str(self.main_window.zone_cp.toPlainText()),
                            "h" : str(self.main_window.zone_h.toPlainText()),
                            "power_in" : str(self.main_window.zone_power_in.toPlainText()),
                            "ambient_temp" : str(self.main_window.zone_ambient_temp.toPlainText()),
                            "initial_temp" : str(self.main_window.zone_initial_temp.toPlainText())}}
        return param

    def __load_params(self, file):
        file_path = os.path.join(self.config_dir, file)
        if self.json_handler.read_json_file(file_path):
            param = self.json_handler.get_data()
            self.main_window.zone_total_time.setPlainText(str(param.get("plate").get("time")))
            self.main_window.zone_lenght.setPlainText(str(param.get("plate").get("lenght")))
            self.main_window.zone_Depth.setPlainText(str(param.get("plate").get("depth")))
            self.main_window.zone_thick.setPlainText(str(param.get("plate").get("thickness")))
            self.main_window.zone_nx.setPlainText(str(param.get("plate").get("nx")))
            self.main_window.zone_ny.setPlainText(str(param.get("plate").get("ny")))
            self.main_window.zone_k.setPlainText(str(param.get("plate").get("k")))
            self.main_window.zone_rho.setPlainText(str(param.get("plate").get("rho")))
            self.main_window.zone_cp.setPlainText(str(param.get("plate").get("cp")))
            self.main_window.zone_h.setPlainText(str(param.get("plate").get("h")))
            self.main_window.zone_power_in.setPlainText(str(param.get("plate").get("power_in")))
            self.main_window.zone_ambient_temp.setPlainText(str(param.get("plate").get("ambient_temp")))
            self.main_window.zone_initial_temp.setPlainText(str(param.get("plate").get("initial_temp")))

#### Public FCT

    def close_window(self):
        self.main_window.close()
        self.__Config_autosave()

    def minimize_window(self):
        self.main_window.showMinimized()

    def show_main_window(self):
        self.main_window.show()

    def show_serial_monitor(self):
        self.serial_window.show()




    def load_params(self):
        self.__load_params(self.main_window.cb_import.currentText())

    def autosave(self):
        self.__Config_autosave()

    def export_params(self):
        default = os.path.join(self.cwd, self.config_dir)
        file_path, _ = QFileDialog.getSaveFileName(
        None,  # Parent window (None means the dialog is standalone)
        "Save JSON File",  # Dialog title
        default,  # Default directory (empty means it opens in the last used directory)
        "JSON Files (*.json);;All Files (*)"  # File filter
        )

        # Check if the user selected a file or canceled
        if not file_path:
            QMessageBox.warning(None, "Export Cancelled", "No file selected for export.")
            return False

        try:
            params = self.__fetch_params()
            return self.json_handler.write_json_file(file_path, params)

        except Exception as e:
            QMessageBox.critical(None, "Export Failed", f"An error occurred while saving:\n{str(e)}")
            return False

    def start_simulation(self):
        params = self.__fetch_params()
        try:
            time = int(params.get("plate").get("time"))
            lenght = int(params.get("plate").get("lenght"))
            depth = int(params.get("plate").get("depth"))
            thickness = float(params.get("plate").get("thickness"))
            nx = int(params.get("plate").get("nx"))
            ny = int(params.get("plate").get("ny"))
            k = float(params.get("plate").get("k"))
            rho = float(params.get("plate").get("rho"))
            cp = float(params.get("plate").get("cp"))
            h = float(params.get("plate").get("h"))
            power_in = float(params.get("plate").get("power_in"))
            ambient_temp = float(params.get("plate").get("ambient_temp"))
            initial_temp = float(params.get("plate").get("initial_temp"))
        except ValueError as err:
            print(err)
        except Exception as err:
            print(err)
            sys.exit(-1)

        try:
            if (time != None) and (lenght != None) and (depth != None) and (thickness != None) and (nx != None) and (ny != None) and (k != None) and (rho != None) and (cp != None) and (h != None) and (power_in != None) and (ambient_temp != None) and (initial_temp != None):
                if (type(time) == int) and (type(lenght) == int) and (type(depth) == int) and (type(thickness) == float) and (type(nx) == int) and (type(ny) == int) and (type(k) == float) and (type(rho) == float) and (type(cp) == float) and (type(h) == float) and (type(power_in) == float) and (type(ambient_temp) == float) and (type(initial_temp) == float):

                    sim = Simulateur(time, lenght, depth, thickness, nx, ny, k, rho,
                        cp, h, power_in, ambient_temp, initial_temp)
        except UnboundLocalError as err:
            print(err)
            print("Value must not correspond to correct type or is empty")
        except Exception as err:
            print(err)
            sys.exit(-1)
 



