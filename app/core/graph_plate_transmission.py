import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.animation import FuncAnimation
from plate_transmission import Plate
import threading

plate = Plate()#nx=24, nz=24)

# Set up the 3D plot
fig = plt.figure()
ax = plt.axes(projection='3d')
last_time = 0
stop = False

def update_plate():
    global last_time, stop
    while not stop:
        plate.update_plate_with_numpy()


# The parameter frame is unused, but is necessary.
def update_plot(frame:int, ax: plt.Axes):
    # Refresh the graph
    ax.clear()
    line = ax.plot_surface(plate.X * 1e3,  plate.Y * 1e3, plate.temps - 273, label="Temperature", cmap=cm.plasma)
    ax.text2D(-0.1, 0.9, f"Simulation Time : {plate.current_time}s", transform=ax.transAxes)
    ax.set_xlabel("Position x [mm]")
    ax.set_ylabel("Position y [mm]")
    ax.set_zlabel("Temperature [°C]")
    ax.set_title("Temperature Distribution Over Time")
    return line,

# Start thread to calculate the propagation
t1 = threading.Thread(target=update_plate)
t1.start()

# This updates the graph every interval (ms)
# The higher the interval, the less frames you will see, but the faster the simulation will be able to update itself
ani = FuncAnimation(fig, update_plot, fargs=(ax,), interval=300, cache_frame_data=True, save_count=10)

plt.show()

# This makes sure that when we close the graph window, the thread stops.
stop = True
t1.join()