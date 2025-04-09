# canvas.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm
import numpy as np

class PlateCanvas(FigureCanvas):
    def __init__(self, step_sim_time, parent=None):
        self.fig = Figure(figsize=(10, 5))
        self.ax_heat = self.fig.add_subplot(221)
        self.ax_t1   = self.fig.add_subplot(222)
        self.ax_t2   = self.fig.add_subplot(223)
        self.ax_t3   = self.fig.add_subplot(224)
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1,
                                 wspace=0.4, hspace=0.4)
        super().__init__(self.fig)
        self.setParent(parent)

        # state updated by the worker
        self.latest_temps = None
        self.latest_time  = 0.0

        # global colour scale
        self.vmin = None
        self.vmax = None
        self.cb   = None

        # traces
        self.times, self.power, self.perturbation, self.t1, self.t2, self.t3 = [], [], [], [], [], []

        # cheap timer just to refresh the figure
        self._redraw_timer = QTimer(self)
        self._redraw_timer.timeout.connect(self._redraw)
        self._redraw_timer.start(int(step_sim_time * 1000))

    # called once from controller after worker is built
    def bind(self, worker, plate):
        self.worker = worker
        self.plate  = plate
        self.worker.updated.connect(self._on_new_data)

        # pre‑compute thermistor indices (mm → matrix)
        self.therm_idx = [
            (round(y / (1e3*plate.dy)), round(x / (1e3*plate.dx)))
            for (x, y) in plate.thermistances_positions
        ]

    # slot: receive fresh array from worker
    def _on_new_data(self, temps_k, current_time, current_power, current_pert):
        self.latest_temps = temps_k - 273.0   # °C
        self.latest_time  = current_time

        # lock‑in global min / max
        tmin, tmax = self.latest_temps.min(), self.latest_temps.max()
        self.vmin = tmin if self.vmin is None else min(self.vmin, tmin)
        self.vmax = tmax if self.vmax is None else max(self.vmax, tmax)

        # update traces
        i1,j1 = self.therm_idx[0]
        i2,j2 = self.therm_idx[1]
        i3,j3 = self.therm_idx[2]
        self.times.append(current_time)
        self.t1.append(self.latest_temps[i1,j1])
        self.t2.append(self.latest_temps[i2,j2])
        self.t3.append(self.latest_temps[i3,j3])
        self.power.append(current_power)
        self.perturbation.append(current_pert)


    # paint everything
    def _redraw(self):
        if self.latest_temps is None:
            return

        # --- heat map ---
        self.ax_heat.clear()
        im = self.ax_heat.imshow(self.latest_temps,
        cmap=cm.plasma,
        origin='lower',
        extent=[
            0, self.plate.lx*1e3,
            0, self.plate.ly*1e3
        ],
        aspect='auto',
        vmin=self.vmin,
        vmax=self.vmax)
        self.ax_heat.set_title(f"Sim time: {self.latest_time:.1f}s")
        self.ax_heat.set_xlabel("X [mm]")
        self.ax_heat.set_ylabel("Y [mm]")

        if self.cb is None:
            self.cb = self.fig.colorbar(im, ax=self.ax_heat, label="Temp [°C]")
        else:
            self.cb.update_normal(im)

        # --- traces ---
        for ax, data, title in [
            (self.ax_t1, self.t1, "Thermistor 1"),
            (self.ax_t2, self.t2, "Thermistor 2"),
            (self.ax_t3, self.t3, "Thermistor 3")
        ]:
            ax.clear()
            ax.plot(self.times, data, 'r-')
            ax.set_title(title)
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Temp [°C]")
            ax.grid(True)

        self.draw()
