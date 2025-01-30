import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parameters
total_time = 500  # Total simulation time [s]
lx = 120e-3  # Length [m]
thickness = 1.5e-3  # Thickness [m]

nx = 120  # Number of elements in x

# Material properties (for Aluminum)
k = 205  # Thermal conductivity [W/m·K]
rho = 2700  # Density [kg/m^3]
cp = 900  # Specific heat capacity [J/kg·K]
alpha = k / (rho * cp)  # Thermal diffusivity [m^2/s]

h_convection = 20  # Convection coefficient [W/m^2·K]
# h_conv = 0  # Uncomment to remove convection

# Calculated parameters
dx = lx / nx  # Discretization step in x [m]
dy = thickness  # Thickness in y [m]
dz = thickness  # Thickness in z [m]

dt = dx**2 / (8 * alpha)  # Time step [s]
nt = round(total_time / dt)  # Number of time iterations

# Geometry parameters
area_ends = dy * dz  # End area [m^2]
area_sides = dx * dz  # Side area [m^2]
area_top = dx * dy  # Top/bottom area [m^2]
volume = dx * dy * dz  # Element volume [m^3]

times = np.arange(0, nt) * dt  # Time vector
position = np.arange(0, nx) * dx  # Position vector

# Power input
power_in = 1.5  # Power [W]
p_in_location_x = int(round((lx / 4) / dx))  # Location of power input
powers = np.zeros(nx)
powers[p_in_location_x] = power_in  # Power applied to one element

# Initial conditions
ambient_temp = 273 + 25.0  # Ambient temperature [K]
temps = np.full(nx, ambient_temp)  # Initial temperature of all elements

temp_location_x = int(round((lx / 2) / dx))  # Location of localized heat
thermistance_location_x = int(round((3 * lx / 4) / dx))  # Location of temperature measurement

# Preallocate vectors
energy_added = np.zeros(nt)
energy_loss = np.zeros(nt)
thermistances = np.zeros(nt)
new_temps = np.zeros_like(temps)

# Set up the 2D plot
fig, ax = plt.subplots(figsize=(10, 6))
line, = ax.plot(position * 1e3, temps - 273, label="Temperature")
ax.set_xlabel("Position [mm]")
ax.set_ylabel("Temperature [°C]")
ax.set_title("Temperature Distribution Over Time")
ax.grid()
ax.legend()

def update_plot(frame:int, ax: plt.Axes):
    global temps, new_temps

    for i in range(nx):
        new_temps[i] = temps[i]

        if i == 0:  # First element
            new_temps[i] += dt / (rho * cp) * k * (temps[i + 1] - temps[i]) / dx**2
            new_temps[i] += dt / (rho * cp) * h_convection * (ambient_temp - temps[i]) * area_ends / volume

        elif i == nx - 1:  # Last element
            new_temps[i] += dt / (rho * cp) * k * (temps[i - 1] - temps[i]) / dx**2
            new_temps[i] += dt / (rho * cp) * h_convection * (ambient_temp - temps[i]) * area_ends / volume

        else:  # Interior elements
            new_temps[i] += dt / (rho * cp) * k * (temps[i + 1] - 2 * temps[i] + temps[i - 1]) / dx**2

        new_temps[i] += dt / (rho * cp) * powers[i] / volume
        new_temps[i] += dt / (rho * cp) * h_convection * (ambient_temp - temps[i]) * 2 * area_sides / volume
        new_temps[i] += dt / (rho * cp) * h_convection * (ambient_temp - temps[i]) * 2 * area_top / volume

    temps[:] = new_temps
    ax.clear()
    line, = ax.plot(position * 1e3, temps - 273, label="Temperature")
    ax.set_xlabel("Position [mm]")
    ax.set_ylabel("Temperature [°C]")
    ax.set_title("Temperature Distribution Over Time")
    ax.grid()
    ax.relim()
    ax.autoscale_view(True, True, True)
    return line,

ani = FuncAnimation(fig, update_plot, fargs=(ax,), interval=10, cache_frame_data=False)
plt.show()