import matplotlib.pyplot as plt
import math

def volt_to_resistance(volt:float):
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


f = open("arduino_output.txt", "r")

time = []
thermistance1 = []
thermistance2 = []
thermistance3 = []

for line in f:
    eachItem = line.split(', ')
    time.append(float(eachItem[0])/1000)
    thermistance1.append(resistance_to_temp(volt_to_resistance(float(eachItem[1]))))
    thermistance2.append(resistance_to_temp(volt_to_resistance(float(eachItem[2]))))
    thermistance3.append(resistance_to_temp(volt_to_resistance(float(eachItem[3]))))

plt.plot(time, thermistance1)
plt.plot(time, thermistance2)
plt.plot(time, thermistance3)
plt.show()