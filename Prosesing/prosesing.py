# Python script to plot a heatmap from the given CSV file

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

# Load the CSV file
def load_data(file_path):
    return pd.read_csv(file_path)

# Calculate the mean of the first few frequencies and the difference from the target frequency
def calculate_difference(data, target_freq, num_initial=10):
    first_few_freqs = data.iloc[:, 2:2 + num_initial]
    mean_first_few = first_few_freqs.mean(axis=1)
    difference = data[target_freq] - mean_first_few
    return difference

# Plot the heatmap
def plot_heatmap(ra, dec, difference, target_freq):
    # Group by RA and Dec to handle duplicates and average the differences
    df = pd.DataFrame({'ra': ra, 'dec': dec, 'difference': difference})
    df = df.groupby(['ra', 'dec'], as_index=False).mean()
    pivot = df.pivot(index='dec', columns='ra', values='difference')
    plt.figure(figsize=(8, 6))
    plt.imshow(pivot, aspect='auto', origin='lower', 
               extent=[df['ra'].min(), df['ra'].max(), df['dec'].min(), df['dec'].max()], cmap='viridis')
    plt.colorbar(label='Difference (Target - Mean)')
    plt.title(f'Heatmap of Signal Difference (Target: {target_freq} MHz)')
    plt.xlabel('Right Ascension (RA)')
    plt.ylabel('Declination (Dec)')
    plt.show()

# Main function
def main():
    file_path = 'output.csv'  # Replace with your file path
    data = load_data(file_path)

    # Find the target frequency closest to 1420.54 MHz
    target_freq = min([col for col in data.columns[2:]], key=lambda x: abs(float(x) - 1420.54))

    # Calculate the difference
    difference = calculate_difference(data, target_freq)

    # Extract RA and Dec
    ra = data['ra']
    dec = data['dec']

    # Plot the heatmap
    plot_heatmap(ra, dec, difference, target_freq)
# Update the target frequency and plot the new heatmap
def update_plot(target_freq, num_initial):
    file_path = file_path_var.get()  # Get the file path from input field
    data = load_data(file_path)
    target_freq = min([col for col in data.columns[2:]], key=lambda x: abs(float(x) - target_freq)) #get point closes to target frequinsy
    # Calculate the difference
    difference = calculate_difference(data, target_freq, num_initial)

    # Extract RA and Dec
    ra = data['ra']
    dec = data['dec']

    # Plot the interpolated heatmap
    plot_heatmap(ra, dec, difference, target_freq)
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    file_path_var.set(file_path)

# Main function to create the Tkinter interface
def main_gui():
    global file_path_var

    # Create the main window
    root = tk.Tk()
    root.title("Heatmap Plotter")

    # File path selection
    file_path_var = tk.StringVar()
    file_path_entry = tk.Entry(root, textvariable=file_path_var, width=70)
    file_path_entry.grid(row=0, column=0)
    browse_button = tk.Button(root, text="Browse", command=browse_file, width=10)
    browse_button.grid(row=0, column=1)

    # Slider for target frequency
    target_freq_slider = tk.Scale(root, from_=1418, to_=1422, resolution=0.01, orient=tk.HORIZONTAL, label="Target Frequency (MHz)")
    target_freq_slider.set(1420.7)  # Default value
    target_freq_slider.grid(row=1, column=0, columnspan=2, ipadx=200)

    # Slider for mode area (number of initial frequencies to average)
    mode_area_slider = tk.Scale(root, from_=5, to_=50, orient=tk.HORIZONTAL, label="Mode Area (Initial Frequencies)")
    mode_area_slider.set(10)  # Default value
    mode_area_slider.grid(row=2, column=0, columnspan=2, ipadx=200, pady=10)

    # Update button
    update_button = tk.Button(root, text="Update Plot", command=lambda: update_plot(target_freq_slider.get(), mode_area_slider.get()))
    update_button.grid(row=3, column=0, columnspan=2)

    root.mainloop()

if __name__ == '__main__':
    main_gui()


#if __name__ == '__main__':
   # main()
