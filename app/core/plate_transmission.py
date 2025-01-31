import numpy as np


class Plate:
    def __init__(self, total_time=500, lx=120e-3, lz=120e-3, thickness=1.5e-3, nx=120, nz=120, k=205, rho=2700,
                 cp=900, h_convection=20, power_in=1.5, ambient_temp=25.0, initial_plate_temp=0):
        # Parameters
        self.total_time = total_time  # Total simulation time [s]
        self.lx = lx  # Length [m]
        self.lz = lz  # Depth  [m]
        self.thickness = thickness  # Thickness [m]

        self.nx = nx  # Number of elements in x
        self.nz = nz  # Number of elements in z

        # Material properties (for Aluminum)
        self.k = k  # Thermal conductivity [W/m·K]
        self.rho = rho  # Density [kg/m^3]
        self.cp = cp  # Specific heat capacity [J/kg·K]
        self.alpha = k / (rho * cp)  # Thermal diffusivity [m^2/s]
        print(self.alpha)

        self.h_convection = h_convection  # Convection coefficient [W/m^2·K]

        # Calculated parameters
        self.dx = lx / nx  # Discretization step in x [m]
        self.dy = thickness  # Thickness in y [m]
        self.dz = lz / nz  # Discretization step in z [m]

        # TODO: Validate if this should change when in 2D (for now we don't even use dt)
        self.dt = self.dx**2 / (8 * self.alpha)  # Time step [s]
        self.nt = round(self.total_time / self.dt)  # Number of time iterations

        # Geometry parameters
        #  z +--------------+       y ^   
        #   /              /|         |  ↗ z
        #y +--------------+ +         | /
        #  |              |/          |/
        #  +--------------+ x         +------->x
        self.area_ends = self.dx * self.dy  # End area [m^2]
        self.area_sides = self.dy * self.dz  # Side area [m^2]
        self.area_top = self.dx * self.dz  # Top/bottom area [m^2]
        self.volume = self.dx * self.dy * self.dz  # Element volume [m^3]

        self.times = np.arange(0, self.nt) * self.dt  # Time vector
        
        x = np.arange(0, self.nx) * self.dx
        z = np.arange(0, self.nz) * self.dz
        self.X, self.Z = np.meshgrid(x, z)

        # Power input
        self.power_in = power_in  # Power [W]
        self.p_in_location = (int(round((lx / 4) / self.dx)), int(round((lz / 2) / self.dx)))  # Location of power input (quarter of the length)
        self.powers = np.zeros([nx, nz])
        self.powers[self.p_in_location] = power_in  # Power applied to one element

        # Initial conditions
        self.ambient_temp = 273.0 + ambient_temp  # Ambient temperature [K]
        self.temps = np.full([nx, nz], self.ambient_temp + initial_plate_temp)  # Initial temperature of all elements in x

        self.temp_location = (int(round((lx / 2) / self.dx)), int(round((lz / 2) / self.dz)))  # Location of localized heat
        self.thermistance_location = (int(round((3 * lx / 4) / self.dx)), int(round((3 * lz / 4) / self.dz)))  # Location of temperature measurement

        # Preallocate vectors
        self.new_temps = np.zeros_like(self.temps)
        self.dt_alpha = self.dt / (self.rho * self.cp) * self.k
        self.dt_conv = self.dt / (self.rho * self.cp) * self.h_convection
        
        
    
    def update_plate(self):
        for i in range(self.nx):
            for j in range(self.nz):
                self.new_temps[i, j] = self.temps[i, j]

                if i == 0:  # First column
                    if j == 0: # First row
                        # We have to add right, up and then air to the left and down.
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i + 1, j] - self.temps[i, j]) / self.dx**2 # right
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i, j + 1] - self.temps[i, j]) / self.dz**2 # up
                        
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_ends / self.volume # down
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_sides / self.volume # left
                    elif j == self.nz - 1: # Last row    
                        # Add right, down and air to the left and up
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i + 1, j] - self.temps[i, j]) / self.dx**2 # right
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i, j - 1] - self.temps[i, j]) / self.dz**2 # down
                        
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_sides / self.volume # left
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_ends / self.volume # up
                    else:
                        # Add right, up, down and air to the left only
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i + 1, j] - self.temps[i, j]) / self.dx**2 # right
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i, j + 1] - self.temps[i, j]) / self.dx**2 # up
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i, j - 1] - self.temps[i, j]) / self.dx**2 # down
                        
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * (self.area_sides) / self.volume # left

                elif i == self.nx - 1:  # Last element
                    if j == 0: # First row
                        # We have to add left, up and then air to the right and down.
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i - 1, j] - self.temps[i, j]) / self.dx**2 # left
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i, j + 1] - self.temps[i, j]) / self.dx**2 # up
                        
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_sides / self.volume # right
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_ends / self.volume # down
                    elif j == self.nz - 1: # Last row    
                        # Add left, down and air to the right and up
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i - 1, j] - self.temps[i, j]) / self.dx**2 # left
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i, j - 1] - self.temps[i, j]) / self.dx**2 # down
                        
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_sides / self.volume # right
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_ends / self.volume # up
                    else:
                        # Add left, up, down and air to the right only
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i - 1, j] - self.temps[i, j]) / self.dx**2 # left
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i, j + 1] - self.temps[i, j]) / self.dx**2 # up
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i, j - 1] - self.temps[i, j]) / self.dx**2 # down
                        
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_sides / self.volume # right

                else:  # Interior elements
                    if j == 0: # First row
                        # We have to add left, right, up and then air down.
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i - 1, j] - self.temps[i, j]) / self.dx**2 # left
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i + 1, j] - self.temps[i, j]) / self.dx**2 # right
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i, j + 1] - self.temps[i, j]) / self.dz**2 # up
                        
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_ends / self.volume # down
                    elif j == self.nz - 1: # Last row    
                        # Add left right, down and air up
                        self.new_temps[i, j] += self.dt_alpha * (
                            (self.temps[i - 1, j] - self.temps[i, j]) + # left
                            (self.temps[i + 1, j] - self.temps[i, j]) + # right
                            self.temps[i, j - 1] - self.temps[i, j]) / self.dz**2 # down
                        
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_ends / self.volume # up
                    else:
                        # Add left, right, up and down
                        self.new_temps[i, j] += self.dt_alpha * (
                            (self.temps[i + 1, j] - self.temps[i, j]) + # right
                            (self.temps[i, j + 1] - self.temps[i, j]) + # up
                            (self.temps[i, j - 1] - self.temps[i, j]) + # down
                            (self.temps[i - 1, j] - self.temps[i, j])) / self.dx**2 # left

                # Add power
                self.new_temps[i, j] += self.dt / (self.rho * self.cp) * self.powers[i, j] / self.volume
                
                self.new_temps[i, j] += self.dt_conv * (self.ambient_temp - self.temps[i, j]) * 2 * self.area_top / self.volume

        self.temps[:] = self.new_temps
