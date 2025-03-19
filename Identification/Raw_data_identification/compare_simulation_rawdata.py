import matplotlib.pyplot as plt

f = open("essaie2_temp.txt", "r")

test_time = []
test_temp1 = []
test_temp2 = []
test_temp3 = []

for line in f:
    eachItem = line.split(' ')
    test_time.append(float(eachItem[0]))
    test_temp1.append(float(eachItem[2]))
    test_temp2.append(float(eachItem[3]))
    test_temp3.append(float(eachItem[4]))

nomfichier = "thermistance3_temp_thick1.82_rho2333.txt"
f = open(nomfichier, "r")

simul_time = []
simul_temp1 = []
simul_temp2 = []
simul_temp3 = []

for line in f:
    eachItem = line.split(' ')
    simul_time.append(float(eachItem[0]))
    simul_temp1.append(float(eachItem[1]))
    simul_temp2.append(float(eachItem[2]))
    simul_temp3.append(float(eachItem[3]))
    
plt.title("Corrélation simulation, réalité")
plt.xlabel("Temps (s)")
plt.ylabel("Température aux thermistances (°C)")
plt.plot(test_time, test_temp1)
plt.plot(test_time, test_temp2)
plt.plot(test_time, test_temp3)
plt.plot(simul_time, simul_temp1)
plt.plot(simul_time, simul_temp2)
plt.plot(simul_time, simul_temp3)

plt.show()