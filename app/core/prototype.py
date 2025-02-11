import numpy as np
from plate_transmission import Plate

# Initialisation de la plaque
plate = Plate()

# Nombre de pas de simulation
num_steps = 10000  # Ajuste selon tes besoins

# Stockage des résultats
temps_list = []
time_list = []

for _ in range(num_steps):
    plate.update_plate_with_numpy()
    temps_list.append(plate.temps.copy())  # Sauvegarde des températures
    time_list.append(plate.current_time)   # Sauvegarde du temps actuel

# Conversion en tableaux numpy
temps_array = np.array(temps_list)
time_array = np.array(time_list)

# Sauvegarde des données dans un fichier compressé
np.savez_compressed("temperature_data.npz", temps=temps_array, time=time_array, X=plate.X, Y=plate.Y)

print("Simulation terminée. Les données ont été enregistrées.")

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.animation import FuncAnimation

# Chargement des données
data = np.load("temperature_data.npz")
temps = data["temps"]
time = data["time"]
X = data["X"]
Y = data["Y"]

# Création de la figure
fig = plt.figure()
ax = plt.axes(projection='3d')

# Configuration de la surface initiale
surf = ax.plot_surface(X * 1e3, Y * 1e3, temps[0] - 273, cmap=cm.plasma)

# Mise à jour du graphique à chaque frame
def update_plot(frame):
    ax.clear()
    ax.plot_surface(X * 1e3, Y * 1e3, temps[frame] - 273, cmap=cm.plasma)
    ax.set_xlabel("Position [mm]")
    ax.set_ylabel("Position [mm]")
    ax.set_zlabel("Température [°C]")
    ax.set_title(f"Évolution de la température (t = {time[frame]:.2f}s)")

# Création de l’animation
ani = FuncAnimation(fig, update_plot, frames=range(0, len(time), 1000), interval=1) # On pourra ajuster interval selon nos besoins

# Affichage de l’animation
plt.show()
