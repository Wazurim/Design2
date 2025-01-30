import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from plate_transmission import Plate

plate = Plate()

# Set up the 2D plot
fig, ax = plt.subplots(figsize=(10, 6))

# The parameter frame is unused, but is necessary.
def update_plot(frame:int, ax: plt.Axes):
    # Update the plate
    plate.update_plate()
    
    # Refresh the graph
    ax.clear()
    line, = ax.plot(plate.positions * 1e3, plate.temps - 273, label="Temperature")
    ax.set_xlabel("Position [mm]")
    ax.set_ylabel("Temperature [°C]")
    ax.set_title("Temperature Distribution Over Time")
    ax.grid()
    ax.relim()
    ax.autoscale_view(True, True, True)
    return line,

ani = FuncAnimation(fig, update_plot, fargs=(ax,), interval=10, cache_frame_data=False)
plt.show()