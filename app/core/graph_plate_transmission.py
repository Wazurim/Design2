import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.animation import FuncAnimation
from plate_transmission import Plate

plate = Plate(power_in=10)#, h_convection=10000)#, k=20000, h_convection=1000)

# Set up the 3D plot
# fig, ax = plt.subplots(figsize=(10, 6))
fig = plt.figure()
ax = plt.axes(projection='3d')

# The parameter frame is unused, but is necessary.
def update_plot(frame:int, ax: plt.Axes):
    # Update the plate
    plate.update_plate()
    
    # Refresh the graph
    ax.clear()
    # print(plate.temps[10,10])
    line = ax.plot_surface(plate.X * 1e3,  plate.Z * 1e3, plate.temps - 273, label="Temperature", cmap=cm.coolwarm)
    ax.set_xlabel("Position [mm]")
    ax.set_ylabel("Position [mm]")
    ax.set_zlabel("Temperature [°C]")
    ax.set_title("Temperature Distribution Over Time")
    ax.grid()
    # ax.relim()
    # ax.autoscale_view(True, True, True)
    return line,

ani = FuncAnimation(fig, update_plot, fargs=(ax,), interval=10, cache_frame_data=False)
plt.show()