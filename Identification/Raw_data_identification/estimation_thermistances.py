import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

f = open("essaie2_temp.txt", "r")

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
    estimate_2.append((0.0259 * (temp1[i-5] - 25) + 0.9672 * (estimate_2[i-1]-25))+25)

estimate_3 = [temp3[0], temp3[1], temp3[2]]
for i in range(3, len(temp2)):
    estimate_3.append(((0.027 * (temp2[i-3]-25) + 0.9672 * (estimate_3[i-1]-25)))+25)
    

# def test_fitting(x, a, b, c):
#     return ((0.027 * (x[i-3]-25) + 0.9672 * (estimate_3[i-1]-25)))+25
#     # return a * x**2 + b * x + c


# param, param_cov = curve_fit(test_fitting, temp2, y)
plt.plot(time, estimate_3)
plt.plot(time, temp3)
# plt.plot(time, temp2)
# plt.plot(time, estimate_2)

plt.legend(['estimated t3 from t2', 't3'])#,'t2', 'estimated t2 from t1'])
plt.show()

difference = abs(np.subtract(temp3, estimate_3))

diff_mean = np.mean(difference)
print(diff_mean)

plt.plot(time, difference)
plt.show()