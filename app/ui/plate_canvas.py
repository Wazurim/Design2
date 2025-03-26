from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm

class PlateCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 5))
        self.ax3d = self.fig.add_subplot(221, projection='3d')
        self.ax2d1 = self.fig.add_subplot(222)
        self.ax2d2 = self.fig.add_subplot(223)
        self.ax2d3 = self.fig.add_subplot(224)
        self.fig.subplots_adjust(
            left=0.1, right=0.9,    # shrink width-wise
            top=0.9, bottom=0.1,    # shrink height-wise
            wspace=0.4, hspace=0.4    # space between plots
        )

        super().__init__(self.fig)
        self.setParent(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

    def start_simulation(self, plate):
        self.plate = plate
        self.times = []
        self.thermistor_temps1 = []
        self.thermistor_temps2 = []
        self.thermistor_temps3 = []
        self.timer.start(100)

    def update_plot(self):
        step_sim_time = 0.5
        steps = int(step_sim_time / self.plate.dt)

        for _ in range(steps):
            self.plate.update_plate_with_numpy()

        self.ax3d.clear()
        temps_c = self.plate.temps - 273
        self.ax3d.plot_surface(
            self.plate.X * 1e3, self.plate.Y * 1e3, temps_c,
            cmap=cm.plasma
        )
        self.ax3d.set_title(f"Sim Time: {self.plate.current_time:.1f}s")
        self.ax3d.set_xlabel("X [mm]")
        self.ax3d.set_ylabel("Y [mm]")
        self.ax3d.set_zlabel("Temp [°C]")

        self.times.append(self.plate.current_time)
        temp1 = self.plate.temps[self.plate.thermistances_positions[0]] - 273
        self.thermistor_temps1.append(temp1)
        temp2 = self.plate.temps[self.plate.thermistances_positions[1]] - 273
        self.thermistor_temps2.append(temp2)
        temp3 = self.plate.temps[self.plate.thermistances_positions[2]] - 273
        self.thermistor_temps3.append(temp3)

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
