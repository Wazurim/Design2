import matplotlib.pyplot as plt
import numpy as np

f = open("dimanche_test_echelon_lache.txt", "r")

time = []
u = []
temp1 = []
temp2 = []
temp3 = []

for line in f:
    eachItem = line.split()
    time.append(float(eachItem[0])/1000)
    u.append(float(eachItem[1]))
    temp1.append(float(eachItem[2]))
    temp2.append(float(eachItem[3]))
    temp3.append(float(eachItem[4]))

estimate_2 = [temp2[0], temp2[1], temp2[2], temp2[3], temp2[4]]

for i in range(5, len(temp1)):
    estimate_2.append((0.023 * (temp1[i-5] - 25) + 0.9672 * (estimate_2[i-1]-25))+25)

estimate_3 = [temp3[0], temp3[1], temp3[2]]

for i in range(3, len(temp2)):
    estimate_3.append(((0.04431 * (temp2[i-1]-25) + 0.9519 * (estimate_3[i-1]-25)))+25)


estimate_3_1 = [temp3[0], temp3[1]]

for i in range(2, len(temp1)):
    estimate_3_1.append(((0.984 * (estimate_3_1[i-1]-25) + 0.01171 * (temp1[i-1]-25)))+25)


# plt.plot(time, estimate_3)
# plt.plot(time, temp3)
# plt.plot(time, temp2)
# plt.plot(time, estimate_2)

plt.plot(time, estimate_3_1)
plt.plot(time, temp3)


plt.legend(['estimated t3 from t1', 't3'])
plt.show()

difference = abs(np.subtract(temp3, estimate_3_1))

diff_mean = np.mean(difference)
print(diff_mean)

plt.plot(time, difference)
plt.show()