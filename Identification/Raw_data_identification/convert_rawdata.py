import matplotlib.pyplot as plt
import math
import numpy as np

def volt_to_resistance(volt:float):
    # volt = 5 - volt
    # resistance = 2000*volt/(1-volt/5)
    resistance = 5 * (10000-2000 * volt)/volt
    return resistance


A1 = 0.003354016434680530000
B1 = 0.000256523550896126000
C1 = 0.000002605970120720520
D1 = 0.000000063292612648746
RT = 10000


def resistance_to_temp(res:float):
    temp = 1/(A1 + B1 * math.log(RT/res) + C1 * math.log(RT/res)**2 + D1 * math.log(RT/res)**3) - 273.15
    return temp


f = open("arduino_output_essaie2.txt", "r")

time = []
thermistance1 = []
thermistance2 = []
thermistance3 = []

for line in f:
    eachItem = line.split(', ')
    time.append(float(eachItem[0])/1000)
    thermistance1.append(float(eachItem[1]))
    thermistance2.append(float(eachItem[2]))
    thermistance3.append(float(eachItem[3]))

u = np.append(np.zeros(10), np.ones(1027) * -0.824)
u = np.append(u, np.zeros(len(time) - 10 - 1027))

np.savetxt('essaie2_temp_volt.txt', np.c_[time, u, thermistance1, thermistance2, thermistance3])

plt.grid()
plt.xlabel("Temps en seconde")
plt.ylabel("Température en celsius")
plt.title("Test d'échelon -0.824 ampères")
plt.plot(time, u)
plt.plot(time, thermistance1)
plt.plot(time, thermistance2)
plt.plot(time, thermistance3)
plt.show()