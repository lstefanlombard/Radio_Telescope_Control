import os
import time
import matplotlib.pyplot as plt

folder_path = input("Enter the path to the folder containing Datahlin files: ")

plt.figure(figsize=(10, 6))
for filename in sorted(os.listdir(folder_path)):
    if filename.startswith("Datahlin_") and filename.endswith(".txt"):
        file_path = os.path.join(folder_path, filename)
        frequencies = []
        intensities = []

        with open(file_path, 'r') as file:
            lines = file.readlines()[1:]  # Skip the first line (header)
            for line in lines:
                try:
                    parts = line.strip().split()
                    # Check if line contains exactly two float numbers
                    if len(parts) == 2:
                        frequency = float(parts[0])
                        intensity = float(parts[1])
                        frequencies.append(frequency)
                        intensities.append(intensity)
                except (IndexError, ValueError):
                    continue  # Skip malformed lines

        if frequencies and intensities:
            plt.clf()  # Clear the previous plot
            plt.plot(frequencies, intensities, label=filename)
            plt.xlabel("Frequency (MHz)")
            plt.ylabel("Intensity")
            plt.title(f"Plot of {filename}")
            plt.legend()
            plt.pause(1)  # Update the plot every second

plt.show()
