import numpy as np


class Plate:#117.21, 61.6
    def __init__(self, total_time=500, lx=116.44e-3, ly=61.68e-3, thickness=1.82e-3, n=117, k=350, rho=2333,
                    cp=896, h_convection=13.5, amp_in=-0.824, power_transfer=-1.3, ambient_temp=23.8, initial_plate_temp=0,
                    position_heat_source=(16, 31), positions_thermistances=[(16, 31), (61, 31), (106, 31)],
                    start_heat_time=10, stop_heat_time=1027, perturbation =0, position_perturbation=(30, 31), start_perturbation=0, stop_perturbation=1027):
        """ Initialize the plate with the given parameters.
        The plate is a 2D grid of elements, each with its own temperature. The simulation runs for a specified total time, 
        with a given time step. The plate has a specified length, width, and thickness, as well as material properties such as thermal conductivity,
        density, and specific heat capacity. The plate is subject to convection and power input, which can be adjusted over time.
        The plate also has a specified ambient temperature and initial temperature, as well as locations for heat sources and thermistors.
        The simulation can also include perturbations in power input at specified times and locations.

        Args:
            total_time (int, optional): _description_. Defaults to 500.
            lx (_type_, optional): _description_. Defaults to 116.44e-3.
            ly (_type_, optional): _description_. Defaults to 61.68e-3.
            thickness (_type_, optional): _description_. Defaults to 1.82e-3.
            n (int, optional): _description_. Defaults to 117.
            k (int, optional): _description_. Defaults to 350.
            rho (int, optional): _description_. Defaults to 2333.
            cp (int, optional): _description_. Defaults to 896.
            h_convection (float, optional): _description_. Defaults to 13.5.
            amp_in (float, optional): _description_. Defaults to -0.824.
            power_transfer (float, optional): _description_. Defaults to -1.3.
            ambient_temp (float, optional): _description_. Defaults to 23.8.
            initial_plate_temp (int, optional): _description_. Defaults to 0.
            position_heat_source (tuple, optional): _description_. Defaults to (16, 31).
            positions_thermistances (list, optional): _description_. Defaults to [(16, 31), (61, 31), (106, 31)].
            start_heat_time (int, optional): _description_. Defaults to 10.
            stop_heat_time (int, optional): _description_. Defaults to 1027.
            perturbation (int, optional): _description_. Defaults to 0.
            position_perturbation (tuple, optional): _description_. Defaults to (30, 31).
            start_perturbation (int, optional): _description_. Defaults to 0.
            stop_perturbation (int, optional): _description_. Defaults to 1027.
        """

        # Parameters
        self.total_time = total_time  # Total simulation time [s]
        self.lx = lx  # Length [m]
        self.ly = ly  # Width  [m]
        self.thickness = thickness  # Thickness [m]
        self.current_power = 0.0 # Current power [W]
        self.current_pert = 0.0 # Current perturbation [W]

        self.nx = n  # Number of elements in x
        self.ny = round((ly * n)/lx) # Number of elements in y should be proportional to number of elements in x

        # Material properties (for Aluminum)
        self.k = k  # Thermal conductivity [W/m·K]
        self.rho = rho  # Density [kg/m^3]
        self.cp = cp  # Specific heat capacity [J/kg·K]
        self.alpha = k / (rho * cp)  # Thermal diffusivity [m^2/s]

        self.h_convection = h_convection  # Convection coefficient [W/m^2·K]

        # Calculated parameters
        self.dx = lx / self.nx    # Discretization step in x [mm]
        self.dy = ly / self.ny    # Discretization step in y [mm]
        self.dz = thickness  # Thickness in z [m]

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
        self.X, self.Y = np.meshgrid(y, x)

        # Power input
        self.power_in = amp_in * power_transfer  # Power [W]
        self.power_perturbation = perturbation # Power perturbation [W]
        self.pert_location = (round(position_perturbation[0]/(self.dy*1000)), round(position_perturbation[1]/(self.dx*1000)))   # Position of the perturbation in the grid
        self.p_in_location = (round(position_heat_source[0]/(self.dx*1000)), round(position_heat_source[1]/(self.dy*1000))) # Position of the heat source in the grid
        self.powers = np.zeros([self.nx, self.ny]) # Preallocate power array
        self.powers[self.p_in_location] = self.power_in  # Power applied to one element
        self.powers_pert = np.zeros([self.nx, self.ny]) # Preallocate power perturbation array
        self.powers_pert[self.pert_location] = self.power_perturbation  # Power applied to one element
        self.start_heat_time = start_heat_time 
        self.stop_heat_time = stop_heat_time
        self.start_pert = start_perturbation
        self.stop_pert = stop_perturbation

        # Initial conditions
        self.ambient_temp = 273.0 + ambient_temp  # Ambient temperature [K]
        self.temps = np.full([self.nx, self.ny], self.ambient_temp + initial_plate_temp)  # Initial temperature of all elements in x #todo double check initial temp

        self.thermistances_positions = positions_thermistances  # Location of temperature measurement

        # Preallocate vectors
        self.new_temps = np.zeros_like(self.temps)
        self.dt_alpha = self.dt / (self.rho * self.cp) * self.k
        self.dt_conv = self.dt / (self.rho * self.cp) * self.h_convection
        self.current_time = 0
        

    def update_plate_with_numpy(self):
        """Progress the simulation 1 tick using numpy matrix

        Returns:
            np.array: Array of the temps
        """
        # Copy temperatures to avoid modifying the array while computing
        self.new_temps[:] = self.temps[:]

        # Compute interior updates using array slicing
        dT_x = (np.roll(self.temps, shift=-1, axis=0) + np.roll(self.temps, shift=1, axis=0) - 2 * self.temps) / self.dx**2
        dT_y = (np.roll(self.temps, shift=-1, axis=1) + np.roll(self.temps, shift=1, axis=1) - 2 * self.temps) / self.dy**2

        # Apply only inner propagation
        self.new_temps[1:-1, 1:-1] += self.dt_alpha * (dT_x[1:-1, 1:-1] + dT_y[1:-1, 1:-1])

        # Apply convection boundary conditions
        self.new_temps += self.dt_conv * (self.ambient_temp - self.temps) * 2 * self.area_top / self.volume
        
        # Apply power term if it's time to heat up
        if (self.current_time >= self.start_heat_time and self.current_time < self.stop_heat_time):
            self.new_temps += self.dt / (self.rho * self.cp) * self.powers / self.volume
            self.current_power = float(self.power_in)
        else:
            self.current_power = 0.0

        if (self.current_time >= self.start_pert  and self.current_time < self.stop_pert):
            self.new_temps += self.dt / (self.rho * self.cp) * self.powers_pert / self.volume
            self.current_pert = float(self.power_perturbation)
        else:
            self.current_pert = 0.0
        
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

        return self.temps
        
    