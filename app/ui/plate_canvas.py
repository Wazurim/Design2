from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm

class PlateCanvas(FigureCanvas):
    def __init__(self, parent=None, step_sim_time=0.5):
        self.fig = Figure(figsize=(10, 5))
        self.ax3d = self.fig.add_subplot(121, projection='3d')

        self.step_sim_time = step_sim_time 
        self.ax2d1 = self.fig.add_subplot(122)
        #self.ax2d2 = self.fig.add_subplot(223)
        #self.ax2d3 = self.fig.add_subplot(224)
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
        self.timer.start(1)

        self.ax3d.set_xlim(0, 120)
        self.ax3d.set_ylim(0, 120) 
        self.ax3d.set_autoscalex_on(False)
        self.ax3d.set_autoscaley_on(False)
        self.ax3d.set_autoscalez_on(True)
        self.ax3d.autoscale_view(scalex=False, scaley=False, scalez=True)
        #self.ax3d.view_init(elev=25, azim=25)
        self.fig.canvas.draw_idle()   

    def update_plot(self):
        steps = int(self.step_sim_time / self.plate.dt)
        for _ in range(steps):
            self.plate.update_plate_with_numpy()

        self.ax3d.clear()
        self.ax3d.set_xlim(0, 120)
        self.ax3d.set_ylim(0, 120)
        self.ax3d.set_autoscalex_on(False)
        self.ax3d.set_autoscaley_on(False)
        self.ax3d.set_autoscalez_on(True)
        self.ax3d.autoscale_view(scalex=False, scaley=False, scalez=True)
        temps_c = self.plate.temps - 273
        self.ax3d.plot_surface(
            self.plate.Y * 1e3, self.plate.X * 1e3, temps_c,
            cmap=cm.plasma
        )
        self.ax3d.set_title(f"Sim Time: {self.plate.current_time:.1f}s")
        self.ax3d.set_xlabel("X [mm]")
        self.ax3d.set_ylabel("Y [mm]")
        self.ax3d.set_zlabel("Temp [°C]")

        post1 = (round(self.plate.thermistances_positions[0][0] / (1000*self.plate.dx)), round(self.plate.thermistances_positions[0][1] / (1000*self.plate.dy)))
        post2 = (round(self.plate.thermistances_positions[1][0] / (1000*self.plate.dx)), round(self.plate.thermistances_positions[1][1] / (1000*self.plate.dy)))
        post3 = (round(self.plate.thermistances_positions[2][0] / (1000*self.plate.dx)), round(self.plate.thermistances_positions[2][1] / (1000*self.plate.dy)))


        t1 = self.plate.temps[post1] - 273
        t2 = self.plate.temps[post2] - 273
        t3 = self.plate.temps[post3] - 273

        self.times.append(self.plate.current_time)
        self.thermistor_temps1.append(t1)
        self.thermistor_temps2.append(t2)
        self.thermistor_temps3.append(t3)

        self.ax2d1.clear()
        self.ax2d1.plot(self.times, self.thermistor_temps1, color='b', label="Thermistor 1")
        self.ax2d1.plot(self.times, self.thermistor_temps2, color='y', label="Thermistor 2")
        self.ax2d1.plot(self.times, self.thermistor_temps3, color='r', label="Thermistor 3")
        self.ax2d1.set_title("Thermistences")
        self.ax2d1.set_xlabel("Temps[s]")
        self.ax2d1.set_ylabel("Temp [°C]")
        self.ax2d1.grid(True)

        self.ax2d1.legend()

        self.draw()
