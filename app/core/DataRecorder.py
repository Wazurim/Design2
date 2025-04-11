import threading
import time

class DataRecorder(threading.Thread):
    def __init__(self, plate, file_name="data_output.csv", interval=1.0):
        """
        Initializes the data recorder.
        
        Args:
            plate: The simulation plate object providing data.
            file_name (str): The output CSV file name.
            interval (float): Time between recordings (in seconds).
        """
        super().__init__()
        self.plate = plate
        self.file_name = file_name
        self.interval = interval
        self._stop_event = threading.Event()
        
        # Initialize the file and write headers.
        with open(self.file_name, "w") as f:
            f.write("time,t1,t2,t3,current_power,current_pert\n")
    
    def run(self):
        """
        Thread run loop: records data at fixed intervals.
        """
        previous_time = None
        while not self._stop_event.is_set():
            # Calculate positions for thermistance points.
            post1 = (round(self.plate.thermistances_positions[0][0] / (1000 * self.plate.dx)),
                     round(self.plate.thermistances_positions[0][1] / (1000 * self.plate.dy)))
            post2 = (round(self.plate.thermistances_positions[1][0] / (1000 * self.plate.dx)),
                     round(self.plate.thermistances_positions[1][1] / (1000 * self.plate.dy)))
            post3 = (round(self.plate.thermistances_positions[2][0] / (1000 * self.plate.dx)),
                     round(self.plate.thermistances_positions[2][1] / (1000 * self.plate.dy)))
            
            # Record temperatures (converted from Kelvin to Celsius).
            t1 = self.plate.temps[post1] - 273
            t2 = self.plate.temps[post2] - 273
            t3 = self.plate.temps[post3] - 273
            
            # Write the current data record to file.
            if previous_time != self.plate.current_time:
                previous_time = self.plate.current_time
                with open(self.file_name, "a") as f:
                    f.write("{},{},{},{},{},{}\n".format(
                        self.plate.current_time,
                        self.plate.current_power,
                        self.plate.current_pert,
                        t1, t2, t3
                    ))
            # Wait for the specified interval or exit if the event is set.
            if self._stop_event.wait(self.interval):
                break
    
    def stop(self):
        """
        Signals the recording thread to stop.
        """
        self._stop_event.set()
