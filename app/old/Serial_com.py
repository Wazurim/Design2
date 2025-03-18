import tkinter as tk
import threading
import serial
import time

class SerialGUI:
    def __init__(self, root, port, baud, fake):
        self.root = root
        self.port = port
        self.baud = baud
        self.ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2)  # Laisser l’Arduino se réinitialiser si nécessaire

        self.running = True
        self.read_thread = threading.Thread(target=self.read_from_port)
        self.read_thread.start()

        # ----- Interface Graphique -----
        # 1. Boutons pour Play, Stop, Reset
        self.btn_play = tk.Button(root, text="Play", command=self.send_play)
        self.btn_play.pack(pady=2)

        self.btn_stop = tk.Button(root, text="Stop", command=self.send_stop)
        self.btn_stop.pack(pady=2)

        self.btn_reset = tk.Button(root, text="Reset", command=self.send_reset)
        self.btn_reset.pack(pady=2)

        # 2. Champs de saisie pour amplitude et fréquence
        #    et un bouton "Send Param"
        self.param_frame = tk.Frame(root)
        self.param_frame.pack(pady=5)

        tk.Label(self.param_frame, text="Commande:").grid(row=0, column=0, padx=5)
        self.entry_con = tk.Entry(self.param_frame, width=8)
        self.entry_con.insert(0, "25.0")  # Valeur par défaut
        self.entry_con.grid(row=0, column=1, padx=5)

        tk.Label(self.param_frame, text="Ki:").grid(row=1, column=0, padx=5)
        self.entry_ki = tk.Entry(self.param_frame, width=8)
        self.entry_ki.insert(0, "1.0")  # Valeur par défaut
        self.entry_ki.grid(row=1, column=1, padx=5)

        tk.Label(self.param_frame, text="Kp:").grid(row=2, column=0, padx=5)
        self.entry_kp = tk.Entry(self.param_frame, width=8)
        self.entry_kp.insert(0, "0.5")  # Valeur par défaut
        self.entry_kp.grid(row=2, column=1, padx=5)

        self.btn_send_param = tk.Button(self.param_frame, text="Send Param", command=self.send_params)
        self.btn_send_param.grid(row=2, column=0, columnspan=2, pady=5)

        # 3. Zone de texte pour afficher ce qui est reçu depuis l’Arduino
        self.output_text = tk.Text(root, height=10, width=50)
        self.output_text.pack(pady=5)

    # Thread secondaire : lecture continue
    def read_from_port(self):
        while self.running:
            line = self.ser.readline().decode('ascii', errors='ignore').strip()
            if line:
                self.root.after(0, self.print_line, line)
        print("Thread de lecture terminé")

    def print_line(self, text):
        # Affiche la donnée reçue dans la zone de texte
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)

    # ----- Méthodes pour envoyer des commandes -----
    def send_play(self):
        self.ser.write(b"p\n")

    def send_stop(self):
        self.ser.write(b"S\n")

    def send_reset(self):
        self.ser.write(b"R\n")

    def send_params(self):
        """
        Récupère l'amplitude et la fréquence saisies,
        et envoie la commande "PARAM C=... I=... K=..." 
        """
        consigne = self.entry_con.get()
        ki = self.entry_ki.get()
        kp = self.entry_kp.get()
        cmd = f"PARAM C={consigne} I={ki} K={kp}\n"
        self.ser.write(cmd.encode('ascii'))
        self.print_line(cmd)

    def close(self):
        """Arrêt propre : stoppe la lecture et ferme le port série."""
        self.running = False
        self.read_thread.join()
        self.ser.close()

def main():
    root = tk.Tk()
    root.title("Exemple Serial + Tkinter: Paramètres")

    # Adapter le port (ex: "COM3" ou "/dev/ttyACM0") et le baudrate
    app = SerialGUI(root, port="COM3", baud=115200, fake=True)

    def on_closing():
        app.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
