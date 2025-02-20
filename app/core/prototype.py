import numpy as np
from plate_transmission import Plate
import matplotlib.pyplot as plt

# Initialisation de la plaque
plate = Plate()

# Définir le temps total de simulation (en secondes)
total_time = 10  # à modifier selon les besoins

# Calculer le nombre d'itérations basé sur dt
num_steps = int(total_time / plate.dt)  # Nombre total d'itérations

# Définir le ratio d'itérations à sauvegarder
save_ratio = 1
save_interval = 1 / save_ratio   # Nombre d'itérations entre chaque sauvegarde

# Stockage des résultats
temps_list = []
time_list = []
thermistances_temps = []

for step in range(num_steps):
    plate.update_plate_with_numpy()

    # On enregistre seulement toutes les `save_interval` itérations
    if step % save_interval == 0:
        # temps_list.append(plate.temps.copy())  # Sauvegarde des températures
        time_list.append(plate.current_time)   # Sauvegarde du temps simulé
        thermistances_temps.append(plate.temps[plate.thermistances_positions[2]])
        print(f"Enregistrement à l'étape {step} / {num_steps}")
        
    

# Conversion en tableaux numpy
temps_array = np.array(temps_list)
time_array = np.array(time_list)

# Sauvegarde des données dans un fichier compressé
# np.savez_compressed("temperature_data.npz", temps=temps_array, time=time_array, X=plate.X, Y=plate.Y)
np.savetxt('thermistance3_temp.txt', np.transpose([time_array, thermistances_temps]))

print(f"Simulation terminée. Temps total simulé : {total_time}s, Nombre total d'itérations : {num_steps}, "
      f"Intervalle de sauvegarde : {save_interval}, Nombre de frames sauvegardées : {len(time_array)}")

plt.plot(time_list, thermistances_temps)
plt.show()


# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib import cm
# from matplotlib.animation import FuncAnimation

# # Chargement des données
# data = np.load("temperature_data.npz")
# temps = data["temps"]
# time = data["time"]
# X = data["X"]
# Y = data["Y"]

# # Création de la figure
# fig = plt.figure()
# ax = plt.axes(projection='3d')

# # Configuration de la surface initiale
# surf = ax.plot_surface(X * 1e3, Y * 1e3, temps[0] - 273, cmap=cm.plasma)

# # Mise à jour du graphique à chaque frame
# def update_plot(frame):
#     ax.clear()
#     ax.plot_surface(X * 1e3, Y * 1e3, temps[frame] - 273, cmap=cm.plasma)
#     ax.set_xlabel("Position [mm]")
#     ax.set_ylabel("Position [mm]")
#     ax.set_zlabel("Température [°C]")
#     ax.set_title(f"Évolution de la température (t = {time[frame]:.2f}s)")

# # Création de l’animation
# ani = FuncAnimation(fig, update_plot, frames=range(0, len(time), 1), interval=1) # On pourra ajuster interval selon nos besoins

# # Affichage de l’animation
# plt.show()
