import serial
import app.app_settings_and_ressources as res

class Serial_com:
    def __init__(self):
        self.ser = serial.Serial(res.SERIAL_PORT, res.SERIAL_BAUD_RATE, timeout=1)

    def send_data(self, data):
        self.ser.write(data.encode("utf-8"))

    def read_data(self):
        return self.ser.readline().decode("utf-8")
    
    def close(self):
        self.ser.close()
