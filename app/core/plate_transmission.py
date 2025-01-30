import numpy as np


class Plate:
    def __init__(self, total_time=500, lx=120e-3, thickness=1.5e-3, nx=120, k=205, rho=2700,
                 cp=900, h_convection=20, power_in=1.5, ambient_temp=25.0):
        # Parameters
        self.total_time = total_time  # Total simulation time [s]
        self.lx = lx  # Length [m]
        self.thickness = thickness  # Thickness [m]

        self.nx = nx  # Number of elements in x

        # Material properties (for Aluminum)
        self.k = k  # Thermal conductivity [W/m·K]
        self.rho = rho  # Density [kg/m^3]
        self.cp = cp  # Specific heat capacity [J/kg·K]
        self.alpha = k / (rho * cp)  # Thermal diffusivity [m^2/s]

        self.h_convection = h_convection  # Convection coefficient [W/m^2·K]
        # h_conv = 0  # Uncomment to remove convection

        # Calculated parameters
        self.dx = lx / nx  # Discretization step in x [m]
        self.dy = thickness  # Thickness in y [m]
        self.dz = thickness  # Thickness in z [m]

        self.dt = self.dx**2 / (8 * self.alpha)  # Time step [s]
        self.nt = round(self.total_time / self.dt)  # Number of time iterations

        # Geometry parameters
        self.area_ends = self.dy * self.dz  # End area [m^2]
        self.area_sides = self.dx * self.dz  # Side area [m^2]
        self.area_top = self.dx * self.dy  # Top/bottom area [m^2]
        self.volume = self.dx * self.dy * self.dz  # Element volume [m^3]

        self.times = np.arange(0, self.nt) * self.dt  # Time vector
        self.positions = np.arange(0, self.nx) * self.dx  # Position vector

        # Power input
        self.power_in = power_in  # Power [W]
        self.p_in_location_x = int(round((lx / 4) / self.dx))  # Location of power input
        self.powers = np.zeros(nx)
        self.powers[self.p_in_location_x] = power_in  # Power applied to one element

        # Initial conditions
        self.ambient_temp = 273.0 + ambient_temp  # Ambient temperature [K]
        self.temps = np.full(nx, self.ambient_temp)  # Initial temperature of all elements

        self.temp_location_x = int(round((lx / 2) / self.dx))  # Location of localized heat
        self.thermistance_location_x = int(round((3 * lx / 4) / self.dx))  # Location of temperature measurement

        # Preallocate vectors
        self.energy_added = np.zeros(self.nt)
        self.energy_loss = np.zeros(self.nt)
        self.thermistances = np.zeros(self.nt)
        self.new_temps = np.zeros_like(self.temps)
        
        
    
    def update_plate(self):
        for i in range(self.nx):
            self.new_temps[i] = self.temps[i]

            if i == 0:  # First element
                self.new_temps[i] += self.dt / (self.rho * self.cp) * self.k * (self.temps[i + 1] - self.temps[i]) / self.dx**2
                self.new_temps[i] += self.dt / (self.rho * self.cp) * self.h_convection * (self.ambient_temp - self.temps[i]) * self.area_ends / self.volume

            elif i == self.nx - 1:  # Last element
                self.new_temps[i] += self.dt / (self.rho * self.cp) * self.k * (self.temps[i - 1] - self.temps[i]) / self.dx**2
                self.new_temps[i] += self.dt / (self.rho * self.cp) * self.h_convection * (self.ambient_temp - self.temps[i]) * self.area_ends / self.volume

            else:  # Interior elements
                self.new_temps[i] += self.dt / (self.rho * self.cp) * self.k * (self.temps[i + 1] - 2 * self.temps[i] + self.temps[i - 1]) / self.dx**2

            self.new_temps[i] += self.dt / (self.rho * self.cp) * self.powers[i] / self.volume
            self.new_temps[i] += self.dt / (self.rho * self.cp) * self.h_convection * (self.ambient_temp - self.temps[i]) * 2 * self.area_sides / self.volume
            self.new_temps[i] += self.dt / (self.rho * self.cp) * self.h_convection * (self.ambient_temp - self.temps[i]) * 2 * self.area_top / self.volume

        self.temps[:] = self.new_temps