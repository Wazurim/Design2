import matplotlib.pyplot as plt
import re
import numpy as np

file_path = "identification_20250330_152944.txt"


time_values = []
pwm_values = []
t1_values = []
t2_values = []
t3_values = []

pattern = re.compile(r"(\d+\.\d+) ms\s+\|.*?PWM duty:\s+([-\d\.]+).*?ADC t1:\s+([-\d\.]+).*?ADC t2:\s+([-\d\.]+).*?ADC t3:\s+([-\d\.]+)")

with open(file_path, "r") as file:
    for line in file:
        match = pattern.search(line)
        if match:
            time_values.append(float(match.group(1))/1000)
            pwm_values.append(float(match.group(2)))
            t1_values.append(float(match.group(3)))
            t2_values.append(float(match.group(4)))
            t3_values.append(float(match.group(5))+0.48)

# np.savetxt('dimanche_test_echelon_lache.txt', np.c_[time_values, pwm_values, t1_values, t2_values, t3_values])

# plt.plot(time_values, pwm_values)
plt.plot(time_values, t1_values)
plt.plot(time_values, t2_values)
plt.plot(time_values, t3_values)
plt.show()
