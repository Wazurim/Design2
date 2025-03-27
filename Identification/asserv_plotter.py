import re
import matplotlib.pyplot as plt

# File path
file_path = "test_asserv.txt"

# Lists to store extracted values
time_values = []
adc_t3_values = []

# Regular expression to match time and ADC t3 values
pattern = re.compile(r"(\d+\.\d+) ms\s+\|.*?ADC t3:\s+([-\d\.]+)")

# Read and parse the file
with open(file_path, "r") as file:
    for line in file:
        match = pattern.search(line)
        if match:
            time_values.append(float(match.group(1)))  
            adc_t3_values.append(float(match.group(2)))




# Plot the data
plt.figure(figsize=(10, 5))
plt.plot(time_values, adc_t3_values, marker="o", linestyle="-", color="b", label="ADC t3")
plt.xlabel("Time (ms)")
plt.ylabel("ADC t3 Value")
plt.title("ADC t3 Readings Over Time")
plt.legend()
plt.grid()
plt.show()
