from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm

class PlateCanvas(FigureCanvas):
    def __init__(self, parent=None, step_sim_time = 0.1):
        self.fig = Figure(figsize=(10, 5))
        self.ax2d_heatmap = self.fig.add_subplot(221)
        self.ax2d1 = self.fig.add_subplot(222)
        self.ax2d2 = self.fig.add_subplot(223)
        self.ax2d3 = self.fig.add_subplot(224)
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1,
                                 wspace=0.4, hspace=0.4)
        self.step_sim_time = step_sim_time 

        super().__init__(self.fig)
        self.setParent(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

        # Track global color scale
        self.global_min_temp = None
        self.global_max_temp = None

        # Keep a reference to the colorbar
        self.cb = None

    def start_simulation(self, plate):
        self.plate = plate
        self.times = []
        self.thermistor_temps1 = []
        self.thermistor_temps2 = []
        self.thermistor_temps3 = []
        self.timer.start(100)

    def update_plot(self):
        steps = int(self.step_sim_time / self.plate.dt)
        for _ in range(steps):
            self.plate.update_plate_with_numpy()

        self.ax2d_heatmap.clear()

        temps_c = self.plate.temps - 273

        # Update global min/max once they are reached
        current_min = temps_c.min()
        current_max = temps_c.max()
        if self.global_min_temp is None:
            self.global_min_temp = current_min
            self.global_max_temp = current_max
        else:
            if current_min < self.global_min_temp:
                self.global_min_temp = current_min
            if current_max > self.global_max_temp:
                self.global_max_temp = current_max

        # Plot the heatmap with fixed min/max
        im = self.ax2d_heatmap.imshow(
            temps_c,
            cmap=cm.plasma,
            origin='lower',
            extent=[
                self.plate.X.min()*1e3, self.plate.X.max()*1e3,
                self.plate.Y.min()*1e3, self.plate.Y.max()*1e3
            ],
            aspect='auto',
            vmin=self.global_min_temp,
            vmax=self.global_max_temp
        )
        self.ax2d_heatmap.set_title(f"Sim Time: {self.plate.current_time:.1f}s")
        self.ax2d_heatmap.set_xlabel("X [mm]")
        self.ax2d_heatmap.set_ylabel("Y [mm]")

        # If colorbar not created yet, create it; otherwise update
        if self.cb is None:
            self.cb = self.fig.colorbar(im, ax=self.ax2d_heatmap, label="Temp [°C]")
        else:
            self.cb.update_normal(im)

        # Log the three thermistor temps
        self.times.append(self.plate.current_time)
        t1 = self.plate.temps[self.plate.thermistances_positions[0]] - 273
        t2 = self.plate.temps[self.plate.thermistances_positions[1]] - 273
        t3 = self.plate.temps[self.plate.thermistances_positions[2]] - 273
        self.thermistor_temps1.append(t1)
        self.thermistor_temps2.append(t2)
        self.thermistor_temps3.append(t3)

        # Plot each thermistor reading
        self.ax2d1.clear()
        self.ax2d1.plot(self.times, self.thermistor_temps1, color='r')
        self.ax2d1.set_title("Thermistor 1 Temp")
        self.ax2d1.set_xlabel("Time [s]")
        self.ax2d1.set_ylabel("Temp [°C]")
        self.ax2d1.grid(True)

        self.ax2d2.clear()
        self.ax2d2.plot(self.times, self.thermistor_temps2, color='r')
        self.ax2d2.set_title("Thermistor 2 Temp")
        self.ax2d2.set_xlabel("Time [s]")
        self.ax2d2.set_ylabel("Temp [°C]")
        self.ax2d2.grid(True)

        self.ax2d3.clear()
        self.ax2d3.plot(self.times, self.thermistor_temps3, color='r')
        self.ax2d3.set_title("Thermistor 3 Temp")
        self.ax2d3.set_xlabel("Time [s]")
        self.ax2d3.set_ylabel("Temp [°C]")
        self.ax2d3.grid(True)

        self.draw()
