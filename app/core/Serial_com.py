import serial
#import app.app_settings_and_ressources as res

#class Serial_com:
#    def __init__(self):
#        #self.ser = serial.Serial(res.SERIAL_PORT, res.SERIAL_BAUD_RATE, timeout=1)#
#
#    def send_data(self, data):
#        self.ser.write(data.encode("utf-8"))

#    def read_data(self):
#        return self.ser.readline().decode("utf-8")
#    
#    def close(self):
#        self.ser.close()


# Open serial connection on COM6 at 9600 baud
ser = serial.Serial('COM6', 9600, timeout=1)

# Open a file to write the output
with open("arduino_output_essaie2.txt", "w") as file:
    try:
        print("Reading from Arduino. Press Ctrl+C to stop.")
        while True:
            # Read a line from the serial port
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(line)
                file.write(line + "\n")
    except KeyboardInterrupt:
        print("Stopping the script.")
    finally:
        ser.close()
