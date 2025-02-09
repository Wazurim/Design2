import numpy as np


class Plate:
    def __init__(self, total_time=500, lx=120e-3, ly=120e-3, thickness=1.5e-3, nx=120, ny=120, k=205, rho=2800,
                 cp=890, h_convection=7, power_in=1.17, ambient_temp=25.0, initial_plate_temp=0):
        # Parameters
        self.total_time = total_time  # Total simulation time [s]
        self.lx = lx  # Length [m]
        self.ly = ly  # Depth  [m]
        self.thickness = thickness  # Thickness [m]

        self.nx = nx  # Number of elements in x
        self.ny = ny  # Number of elements in z

        # Material properties (for Aluminum)
        self.k = k  # Thermal conductivity [W/m·K]
        self.rho = rho  # Density [kg/m^3]
        self.cp = cp  # Specific heat capacity [J/kg·K]
        self.alpha = k / (rho * cp)  # Thermal diffusivity [m^2/s]
        #print(self.alpha)

        self.h_convection = h_convection  # Convection coefficient [W/m^2·K]

        # Calculated parameters
        self.dx = lx / nx    # Discretization step in x [m]
        self.dy = ly / ny    # Discretization step in y [m]
        self.dz = thickness  # Thickness in z [m]

        # TODO: Validate if this should change when in 2D (for now we don't even use dt)
        self.dt = self.dx**2 / (8 * self.alpha)  # Time step [s]
        self.nt = round(self.total_time / self.dt)  # Number of time iterations

        # Geometry parameters
        #  y +--------------+       z ^
        #   /              /|         |  ↗ y
        #z +--------------+ +         | /
        #  |              |/          |/
        #  +--------------+ x         +------->x
        self.area_ends = self.dx * self.dz  # End area [m^2]
        self.area_sides = self.dz * self.dy  # Side area [m^2]
        self.area_top = self.dx * self.dy  # Top/bottom area [m^2]
        self.volume = self.dx * self.dy * self.dz  # Element volume [m^3]

        self.times = np.arange(0, self.nt) * self.dt  # Time vector
     
        x = np.arange(0, self.nx) * self.dx
        y = np.arange(0, self.ny) * self.dy
        self.X, self.Y = np.meshgrid(x, y)

        # Power input
        self.power_in = power_in  # Power [W]
        self.p_in_location = (int(round((lx / 4) / self.dx)), int(round((ly / 2) / self.dx)))  # Location of power input (quarter of the length)
        self.powers = np.zeros([nx, ny])
        self.powers[self.p_in_location] = power_in  # Power applied to one element

        # Initial conditions
        self.ambient_temp = 273.0 + ambient_temp  # Ambient temperature [K]
        self.temps = np.full([nx, ny], self.ambient_temp + initial_plate_temp)  # Initial temperature of all elements in x #todo double check initial temp

        self.temp_location = (int(round((lx / 2) / self.dx)), int(round((ly / 2) / self.dy)))  # Location of localized heat
        self.thermistance_location = (int(round((3 * lx / 4) / self.dx)), int(round((3 * ly / 4) / self.dy)))  # Location of temperature measurement

        # Preallocate vectors
        self.new_temps = np.zeros_like(self.temps)
        self.dt_alpha = self.dt / (self.rho * self.cp) * self.k
        self.dt_conv = self.dt / (self.rho * self.cp) * self.h_convection
        self.current_time = 0
      

    def update_plate_with_numpy(self):
        # Copy temperatures to avoid modifying the array while computing
        self.new_temps[:] = self.temps[:]

        # Compute interior updates using array slicing
        dT_x = (np.roll(self.temps, shift=-1, axis=0) + np.roll(self.temps, shift=1, axis=0) - 2 * self.temps) / self.dx**2
        dT_y = (np.roll(self.temps, shift=-1, axis=1) + np.roll(self.temps, shift=1, axis=1) - 2 * self.temps) / self.dy**2

        # Apply only inner propagation
        self.new_temps[1:-1, 1:-1] += self.dt_alpha * (dT_x[1:-1, 1:-1] + dT_y[1:-1, 1:-1])

        # Apply convection boundary conditions
        self.new_temps += self.dt_conv * (self.ambient_temp - self.temps) * 2 * self.area_top / self.volume
        
        # Apply power term
        self.new_temps += self.dt / (self.rho * self.cp) * self.powers / self.volume
        
        # Boundary handling manually to avoid wrapping from np.roll
        self.new_temps[0, :] += self.dt_conv * (self.ambient_temp - self.temps[0, :]) * self.area_sides / self.volume
        self.new_temps[-1, :] += self.dt_conv * (self.ambient_temp - self.temps[-1, :]) * self.area_sides / self.volume
        self.new_temps[:, 0] += self.dt_conv * (self.ambient_temp - self.temps[:, 0]) * self.area_ends / self.volume
        self.new_temps[:, -1] += self.dt_conv * (self.ambient_temp - self.temps[:, -1]) * self.area_ends / self.volume
        
        # Ensure edges don't reference out-of-bounds indices
        self.new_temps[0, :] += self.dt_alpha * ((self.temps[1, :] - self.temps[0, :]) / self.dx**2)
        self.new_temps[-1, :] += self.dt_alpha * ((self.temps[-2, :] - self.temps[-1, :]) / self.dx**2)
        self.new_temps[:, 0] += self.dt_alpha * ((self.temps[:, 1] - self.temps[:, 0]) / self.dy**2)
        self.new_temps[:, -1] += self.dt_alpha * ((self.temps[:, -2] - self.temps[:, -1]) / self.dy**2)
        self.temps[:] = self.new_temps
        self.current_time += self.dt
        #print(self.current_time)
        
    
    def update_plate(self):
        for i in range(self.nx):
            for j in range(self.ny):
                self.new_temps[i, j] = self.temps[i, j]

                if i == 0:  # First column
                    if j == 0: # First row
                        # We have to add right, up and then air to the left and down.
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i + 1, j] - self.temps[i, j]) / self.dx**2 # right
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i, j + 1] - self.temps[i, j]) / self.dy**2 # up
                        
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_ends / self.volume # down
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_sides / self.volume # left
                    elif j == self.ny - 1: # Last row    
                        # Add right, down and air to the left and up
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i + 1, j] - self.temps[i, j]) / self.dx**2 # right
                        self.new_temps[i, j] += self.dt_alpha * (
                            self.temps[i, j - 1] - self.temps[i, j]) / self.dy**2 # down
                        
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
                    elif j == self.ny - 1: # Last row    
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
                            self.temps[i, j + 1] - self.temps[i, j]) / self.dy**2 # up
                        
                        self.new_temps[i, j] += self.dt_conv * (
                            self.ambient_temp - self.temps[i, j]) * self.area_ends / self.volume # down
                    elif j == self.ny - 1: # Last row    
                        # Add left right, down and air up
                        self.new_temps[i, j] += self.dt_alpha * (
                            (self.temps[i - 1, j] - self.temps[i, j]) + # left
                            (self.temps[i + 1, j] - self.temps[i, j]) + # right
                            self.temps[i, j - 1] - self.temps[i, j]) / self.dy**2 # down
                        
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
        self.current_time += self.dt
        #print(self.current_time)
