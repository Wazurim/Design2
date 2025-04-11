import sys
import re
import time
import serial
import threading
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QPlainTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal

########################################
# Thread for reading data from serial
########################################
class SerialReadThread(threading.Thread):
    def __init__(self, ser, callback):
        """
        :param ser: an open serial.Serial object
        :param callback: function to call with each line read
        """
        super().__init__()
        self.ser = ser
        self.callback = callback
        self.running = True

    def run(self):
        """ Continuously read lines from the serial port. """
        while self.running:
            try:
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    self.callback(line)
            except Exception as e:
                print("Serial error:", e)
                break
        print("Serial reading thread terminated.")

    def stop(self):
        """ Signal the thread to stop. """
        self.running = False


########################################
# Main PyQt Window
########################################
class SerialMonitor(QWidget):
    # Signal for safe UI updates from the serial thread.
    lineReceived = pyqtSignal(str)

    def __init__(self, port="COM6", baudrate=115200, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Design 2 Prototype serial monitor")
        self.setWindowIcon(QIcon("icon.png"))

        # Ensure the data directory exists
        self.data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.recording = False
        self.file = None


        # ----- 1) Open the serial port -----
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # small delay in case Arduino resets on open
        except Exception as e:
            raise RuntimeError(f"Could not open serial port {port}: {e}")

        self.lineReceived.connect(self.append_line)

        # ----- 2) Start a background thread to read incoming data -----
        self.read_thread = SerialReadThread(self.ser, self.on_line_received)
        self.read_thread.start()

        # Recording flag & file handle
        self.recording = False
        self.file = None


        # ----- 3) Build the UI layout -----
         # UI Layouts
        main_layout = QHBoxLayout()  # Horizontal layout to split log & plot
        control_layout = QVBoxLayout()  # Controls on the left
        plot_layout = QVBoxLayout()  # Plot on the right
        #layout = QVBoxLayout()

        # 3.1) Buttons row: Play, Stop, Reset
        btn_layout = QHBoxLayout()
        self.btn_play = QPushButton("Play")
        self.btn_stop = QPushButton("Stop")
        self.btn_reset = QPushButton("Reset")
        self.btn_record = QPushButton("Record")

        btn_layout.addWidget(self.btn_play)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addWidget(self.btn_record)

        #layout.addLayout(btn_layout)

        self.btn_play.clicked.connect(self.send_play)
        self.btn_stop.clicked.connect(self.send_stop)
        self.btn_reset.clicked.connect(self.send_reset)
        self.btn_record.clicked.connect(self.toggle_recording)


        # 3.2) Param row (Amplitude, Frequency) + "Send Param" button
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("Consigne:"))
        self.input_con = QLineEdit("25.0")
        param_layout.addWidget(self.input_con)
        param_layout.addWidget(QLabel("Ki:"))
        self.input_Ki = QLineEdit("1.0")
        param_layout.addWidget(self.input_Ki)
        param_layout.addWidget(QLabel("Kp:"))
        self.input_Kp = QLineEdit("0.5")
        param_layout.addWidget(self.input_Kp)
        self.btn_param = QPushButton("Send Param")
        param_layout.addWidget(self.btn_param)
        control_layout.addLayout(param_layout)
        self.btn_param.clicked.connect(self.send_param)

        # 3.3) A text field to send a raw command
        raw_cmd_layout = QHBoxLayout()
        raw_cmd_layout.addWidget(QLabel("Raw Command:"))
        self.input_raw_cmd = QLineEdit("PARAM C=25.0 I=1.0 K=0.5")
        raw_cmd_layout.addWidget(self.input_raw_cmd)
        self.btn_send_raw = QPushButton("Send")
        raw_cmd_layout.addWidget(self.btn_send_raw)
        control_layout.addLayout(raw_cmd_layout)
        self.btn_send_raw.clicked.connect(self.send_raw_cmd)

        # 3.4) Use QPlainTextEdit for the received data log (more efficient for plain text)
        self.text_area = QPlainTextEdit()
        self.text_area.setReadOnly(True)


         # Add widgets to layouts
        control_layout.addLayout(btn_layout)
        control_layout.addLayout(param_layout)
        control_layout.addLayout(raw_cmd_layout)
        control_layout.addWidget(self.text_area)
        control_layout.addWidget(self.text_area)

        # Create live plot widget
        self.plot_widget = LivePlotWidget()
        plot_layout.addWidget(self.plot_widget)


        # Add layouts to the main layout
        main_layout.addLayout(control_layout, 2)  # Control panel (left side)
        main_layout.addLayout(plot_layout, 3)  # Real-time plot (right side)



        self.setLayout(main_layout)

    ########################################
    # Worker thread callback
    ########################################
    def on_line_received(self, line):
        self.lineReceived.emit(f"[RX] {line}")
        if self.recording and self.file:
            self.file.write(line + "\n")
            self.file.flush()

    ########################################
    # Slot to update the text area (runs in main thread)
    ########################################
    def append_line(self, text):
        self.text_area.appendPlainText(text)

    ########################################
    # Command sending methods
    ########################################
    def send_play(self):
        self._send_line("p")

    def send_stop(self):
        self._send_line("S")

    def send_reset(self):
        self._send_line("PARAM C=25.0 I=1.0 K=0.5")

    def send_param(self):
        con = self.input_con.text().strip()
        Ki = self.input_Ki.text().strip()
        Kp = self.input_Kp.text().strip()
        cmd = f"PARAM C={con} I={Ki} K={Kp}"
        self._send_line(cmd)

    def send_raw_cmd(self):
        raw_cmd = self.input_raw_cmd.text().strip()
        self._send_line(raw_cmd)

    def _send_line(self, data_str):
        if self.ser and self.ser.is_open:
            line = data_str + "\n"
            self.ser.write(line.encode('ascii', errors='ignore'))
            self.text_area.appendPlainText(f"[TX] {data_str}")

    ########################################
    # Toggle Recording
    ########################################
    def toggle_recording(self):
        if self.recording:
            self.recording = False
            if self.file:
                self.file.close()
            self.text_area.appendPlainText("Enregistrement des données fini -> identification")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.data_dir, f"identification_{timestamp}.txt")
            self.file = open(filename, "w")
            self.recording = True
            self.text_area.appendPlainText("Enregistrement des données lancé")

    ########################################
    # Cleanup on close
    ########################################
    def closeEvent(self, event):
        if self.read_thread is not None:
            self.read_thread.stop()
            self.read_thread.join()
        if self.ser and self.ser.is_open:
            self.ser.close()
        if self.file:
            self.file.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = SerialMonitor(port="COM5", baudrate=115200)

    
    
    # Get the primary screen's available geometry
    screen = app.primaryScreen()
    available_rect = screen.availableGeometry()
    
    # For example, set the window size to 80% of the available width and height,
    # and center it on the screen.
    width = int(available_rect.width() * 0.8)
    height = int(available_rect.height() * 0.8)
    x = available_rect.x() + (available_rect.width() - width) // 2
    y = available_rect.y() + (available_rect.height() - height) // 2
    window.setGeometry(x, y, width, height)
    



    window.show()
    sys.exit(app.exec_())


class LivePlotWidget(QWidget):
    """A QWidget that displays a real-time updating Matplotlib plot."""
    
    def __init__(self):
        super().__init__()
        self.time_values = []
        self.adc_t3_values = []

        # Set up Matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.line, = self.ax.plot([], [], "bo-", label="ADC t3")

        self.ax.set_xlabel("Time (µs)")
        self.ax.set_ylabel("ADC t3 Value")
        self.ax.set_title("Real-Time ADC t3 Readings")
        self.ax.legend()
        self.ax.grid()

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def get_latest_file(self):
        """Finds the most recently created/modified identification file."""
        files = [f for f in os.listdir(self.data_dir) if f.startswith("identification_") and f.endswith(".txt")]
        if not files:
            return None
        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(self.data_dir, f)))
        return os.path.join(self.data_dir, latest_file)

    def update_plot(self):
        """Reads the latest file in real-time and updates the plot dynamically."""
        latest_file = self.get_latest_file()
        if not latest_file:
            print("No recorded data files found.")
            return

        print(f"Monitoring file: {latest_file}")
        pattern = re.compile(r"(\d+\.\d+) ms\s+\|.*?ADC t3:\s+([-?\d\.]+)")

        with open(latest_file, "r") as file:
            file.seek(0, os.SEEK_END)  # Move to the end of the file

            while True:
                line_data = file.readline()
                if not line_data:
                    time.sleep(1)  # Wait for new data
                    continue

                match = pattern.search(line_data)
                if match:
                    self.time_values.append(float(match.group(1)) * 1000)  # Convert ms to µs
                    self.adc_t3_values.append(float(match.group(2)))

                    # Update plot
                    self.line.set_xdata(self.time_values)
                    self.line.set_ydata(self.adc_t3_values)
                    self.ax.relim()
                    self.ax.autoscale_view()

                    self.canvas.draw()  # Update the PyQt plot

                # Stop if recording is done (file closed externally)
                if not os.path.exists(latest_file):
                    print("File closed, stopping live plot.")
                    break


if __name__ == "__main__":
    main()
