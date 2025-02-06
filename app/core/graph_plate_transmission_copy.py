import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.animation import FuncAnimation
from app.core.plate_transmission import Plate
import threading

class Simulateur():
    def __init__(self, total_time, lx, ly, thickness, nx, ny, k, rho,
                cp, h_convection, power_in, ambient_temp, initial_plate_temp):
        self.plate = Plate(total_time, lx, ly, thickness, nx, ny, k, rho,
                cp, h_convection, power_in, ambient_temp, initial_plate_temp)
        self.fig = plt.figure()
        self.ax = plt.axes(projection='3d')
        self.last_time = 0
        self.stop = False

        t1 = threading.Thread(target=self.update_plate)
        t1.start()

        self.ani = FuncAnimation(self.fig, self.update_plot, fargs=(self.ax,), interval=300, cache_frame_data=True, save_count=10)

        
        plt.show()

        self.stop = True
        t1.join()

    def update_plate(self):
        while not self.stop:
            self.plate.update_plate_with_numpy()


    # The parameter frame is unused, but is necessary.
    def update_plot(self,frame:int, ax: plt.Axes):
        # Refresh the graph
        self.ax.clear()
        line = ax.plot_surface(self.plate.X * 1e3,  self.plate.Y * 1e3, self.plate.temps - 273, label="Temperature", cmap=cm.plasma)
        self.ax.text2D(-0.1, 0.9, f"Simulation Time : {self.plate.current_time}s", transform=ax.transAxes)
        self.ax.set_xlabel("Position [mm]")
        self.ax.set_ylabel("Position [mm]")
        self.ax.set_zlabel("Temperature [°C]")
        self.ax.set_title("Temperature Distribution Over Time")
        return line,

# Start thread to calculate the propagation


# This updates the graph every interval (ms)
# The higher the interval, the less frames you will see, but the faster the simulation will be able to update itself




# This makes sure that when we close the graph window, the thread stops.
