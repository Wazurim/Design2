import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.animation import FuncAnimation
from plate_transmission import Plate
import threading

plate = Plate()#nx=24, nz=24)

# Set up the 3D plot
fig = plt.figure()

ax1 = fig.add_axes([0.05,0.05,0.3,0.9], projection='3d')
ax2 = fig.add_axes([0.5,0.125,0.4,0.75])
last_time = 0
stop = False

times = []
thermistance_temps = []

def update_plate():
    global last_time, stop
    while not stop:
        plate.update_plate_with_numpy()


# The parameter frame is unused, but is necessary.
def update_plot(frame:int, ax1: plt.Axes, ax2: plt.Axes):
    # Refresh the graph
    # temps_list.append(plate.temps[plate.thermistances_positions[2]])
    
    ax1.clear()
    line = ax1.plot_surface(plate.X * 1e3,  plate.Y * 1e3, plate.temps - 273, label="Temperature", cmap=cm.plasma)
    ax1.text2D(-0.1, 0.9, f"Simulation Time : {plate.current_time}s", transform=ax1.transAxes)
    ax1.set_xlabel("Position x [mm]")
    ax1.set_ylabel("Position y [mm]")
    ax1.set_zlabel("Temperature [°C]")
    ax1.set_title("Temperature Distribution Over Time")
    x = [0, 1, 2, 3]
    y = [1, 3, 4, 5]
    ax2.clear()
    times.append(plate.current_time)
    thermistance_temps.append(plate.temps[plate.thermistances_positions[2]])
    line2 = ax2.plot(times, thermistance_temps)
    return line, line2

# Start thread to calculate the propagation
t1 = threading.Thread(target=update_plate)
t1.start()

# This updates the graph every interval (ms)
# The higher the interval, the less frames you will see, but the faster the simulation will be able to update itself
ani = FuncAnimation(fig, update_plot, fargs=(ax1, ax2,), interval=300, cache_frame_data=True, save_count=10)

plt.show()

# This makes sure that when we close the graph window, the thread stops.
stop = True
t1.join()