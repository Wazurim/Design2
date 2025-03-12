import sys
import time
import serial
import threading

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

    def __init__(self, port="COM3", baudrate=115200, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Design 2 Prototype serial monitor")
        self.setWindowIcon(QIcon("icon.png"))


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

        # ----- 3) Build the UI layout -----
        layout = QVBoxLayout()

        # 3.1) Buttons row: Play, Stop, Reset
        btn_layout = QHBoxLayout()
        self.btn_play = QPushButton("Play")
        self.btn_stop = QPushButton("Stop")
        self.btn_reset = QPushButton("Reset")
        btn_layout.addWidget(self.btn_play)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_reset)
        layout.addLayout(btn_layout)

        self.btn_play.clicked.connect(self.send_play)
        self.btn_stop.clicked.connect(self.send_stop)
        self.btn_reset.clicked.connect(self.send_reset)

        # 3.2) Param row (Amplitude, Frequency) + "Send Param" button
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("Consigne:"))
        self.input_amp = QLineEdit("1.0")
        param_layout.addWidget(self.input_amp)
        param_layout.addWidget(QLabel("Frequence:"))
        self.input_freq = QLineEdit("1")
        param_layout.addWidget(self.input_freq)
        self.btn_param = QPushButton("Send Param")
        param_layout.addWidget(self.btn_param)
        layout.addLayout(param_layout)
        self.btn_param.clicked.connect(self.send_param)

        # 3.3) A text field to send a raw command
        raw_cmd_layout = QHBoxLayout()
        raw_cmd_layout.addWidget(QLabel("Raw Command:"))
        self.input_raw_cmd = QLineEdit("")
        raw_cmd_layout.addWidget(self.input_raw_cmd)
        self.btn_send_raw = QPushButton("Send")
        raw_cmd_layout.addWidget(self.btn_send_raw)
        layout.addLayout(raw_cmd_layout)
        self.btn_send_raw.clicked.connect(self.send_raw_cmd)

        # 3.4) Use QPlainTextEdit for the received data log (more efficient for plain text)
        self.text_area = QPlainTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        self.setLayout(layout)

    ########################################
    # Worker thread callback
    ########################################
    def on_line_received(self, line):
        self.lineReceived.emit(f"[RX] {line}")

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
        self._send_line("R")

    def send_param(self):
        amp = self.input_amp.text().strip()
        freq = self.input_freq.text().strip()
        cmd = f"PARAM C={amp} F={freq}"
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
    # Cleanup on close
    ########################################
    def closeEvent(self, event):
        if self.read_thread is not None:
            self.read_thread.stop()
            self.read_thread.join()
        if self.ser and self.ser.is_open:
            self.ser.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = SerialMonitor(port="COM4", baudrate=115200)
    
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


if __name__ == "__main__":
    main()
