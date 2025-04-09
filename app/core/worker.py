# worker.py
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np

class PlateWorker(QThread):
    updated = pyqtSignal(np.ndarray, float, float, float)          # temps, current_time
    finished = pyqtSignal()

    def __init__(self, plate, step_sim_time):
        super().__init__()
        self.plate = plate
        self.step_sim_time = step_sim_time
        self._running = True

    def run(self):
        steps = int(self.step_sim_time / self.plate.dt)
        while self._running and self.plate.current_time < self.plate.total_time:
            for _ in range(steps):
                self.plate.update_plate_with_numpy()
            self.updated.emit(self.plate.temps.copy(), self.plate.current_time, self.plate.current_power, self.plate.current_pert)
            self.msleep(0)                          # yield to Qt
        self.finished.emit()

    def stop(self):
        self._running = False
