import csv
import matplotlib.pyplot as plt

def parse_tek_csv(filename):
    """
    Reads the CSV file from your oscilloscope and returns two lists:
      time_values: a list of time points (floats)
      voltage_values: a list of measured voltage points (floats)
    """
    time_values = []
    voltage_values = []
    time_init = 0.0
    line = 0
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader: 
            line += 1
            # We expect up to 5 columns, something like:
            # [col0, col1, col2, col3, col4]
            # Some lines might be shorter/longer if the scope saves differently

            # Skip if row is too short or not numeric in the 3rd/4th columns
            # (Python lists are zero-indexed: col3 is row[3], col4 is row[4])
            if len(row) < 1:
                continue

            # row[3] (time) and row[4] (voltage) might be numeric if they're actual data
            # We'll attempt to convert them to float. If it fails, it's metadata.
            try:
                if line == 3:
                    time_init = float(row[0])
                t = float(row[0]) - time_init
                v = float(row[1])
                time_values.append(t)
                voltage_values.append(v)
            except ValueError:
                # This line likely has metadata, so we skip it
                continue

    return time_values, voltage_values

def main():


    # Parse the CSV to get time and voltage
    time_data, voltage_data = parse_tek_csv("SDS00003.CSV")

    # Now plot it
    plt.figure(figsize=(8, 4))
    plt.plot(time_data, voltage_data)
    plt.title("Peigne de Dirac de l'echantillonage")
    plt.xlabel('Temps (s)')
    plt.ylabel('Voltage (V)')
    plt.grid(True)
    #plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
