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
        
        # Update the plate
        # while(plate.current_time < last_time + 1):
        plate.update_plate_with_numpy()

        # last_time += 1
        # print(last_time)

# The parameter frame is unused, but is necessary.
def update_plot(frame:int, ax: plt.Axes):
    # global stop
    # while not stop:
        # t1 = threading.Thread(target=update_plate)
        # t1.start()
    # update_plate()
    # plate.update_plate()
    
    # Refresh the graph
    ax.clear()
    line = ax.plot_surface(plate.X * 1e3,  plate.Z * 1e3, plate.temps - 273, label="Temperature", cmap=cm.plasma)
    ax.set_xlabel("Position [mm]")
    ax.set_ylabel("Position [mm]")
    ax.set_zlabel("Temperature [°C]")
    ax.set_title("Temperature Distribution Over Time")
    return line,

t1 = threading.Thread(target=update_plate)
t1.start()
ani = FuncAnimation(fig, update_plot, fargs=(ax,), interval=1000, cache_frame_data=True, save_count=10)
plt.show()
stop = True
t1.join()