import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

# Load the CSV file
def load_data(file_path):
    return pd.read_csv(file_path)

# Calculate the mean of the first few frequencies and the difference from the target frequency
def calculate_difference(data, target_freq, num_initial=10):
    # Find the column closest to the target frequency
    freq_columns = [float(col) for col in data.columns[2:]]  # Assuming frequencies start from column 2
    closest_freq = min(freq_columns, key=lambda x: abs(x - target_freq))  # Find the closest frequency
    
    # Find the index of the closest frequency column
    closest_freq_index = data.columns.get_loc(str(closest_freq))
    
    first_few_freqs = data.iloc[:, 2:2 + num_initial]
    mean_first_few = first_few_freqs.mean(axis=1)
    
    # Calculate the difference for the closest frequency
    difference = data.iloc[:, closest_freq_index] - mean_first_few
    return difference * 1e6  # Scale up the difference for better visualization

# Plot the heatmap with interpolation
def plot_heatmap(ra, dec, difference, target_freq):
    # Group by RA and Dec to handle duplicates and average the differences
    df = pd.DataFrame({'ra': ra, 'dec': dec, 'difference': difference})
    df = df.groupby(['ra', 'dec'], as_index=False).mean()
    pivot = df.pivot(index='dec', columns='ra', values='difference')
    plt.figure(figsize=(8, 6))
    plt.imshow(pivot, aspect='auto', origin='lower', 
               extent=[df['ra'].min(), df['ra'].max(), df['dec'].min(), df['dec'].max()], 
               cmap='viridis', interpolation='bicubic')
    plt.colorbar(label='Difference (Target - Mean) x1e6')
    plt.title(f'Interpolated Heatmap of Signal Difference (Target: {target_freq} MHz)')
    plt.xlabel('Right Ascension (RA)')
    plt.ylabel('Declination (Dec)')
    plt.show()

# Update the target frequency and plot the new heatmap
def update_plot(target_freq, num_initial):
    file_path = file_path_var.get()  # Get the file path from input field
    data = load_data(file_path)

    # Calculate the difference
    difference = calculate_difference(data, target_freq, num_initial)

    # Extract RA and Dec
    ra = data['ra']
    dec = data['dec']

    # Plot the interpolated heatmap
    plot_heatmap(ra, dec, difference, target_freq)

# Browse and select file
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
    file_path_entry = tk.Entry(root, textvariable=file_path_var, width=50)
    file_path_entry.grid(row=0, column=0)
    browse_button = tk.Button(root, text="Browse", command=browse_file)
    browse_button.grid(row=0, column=1)

    # Slider for target frequency
    target_freq_slider = tk.Scale(root, from_=1418, to_=1422, resolution=0.01, orient=tk.HORIZONTAL, label="Target Frequency (MHz)")
    target_freq_slider.set(1420.7)  # Default value
    target_freq_slider.grid(row=1, column=0, columnspan=2)

    # Slider for mode area (number of initial frequencies to average)
    mode_area_slider = tk.Scale(root, from_=5, to_=20, orient=tk.HORIZONTAL, label="Mode Area (Initial Frequencies)")
    mode_area_slider.set(10)  # Default value
    mode_area_slider.grid(row=2, column=0, columnspan=2)

    # Update button
    update_button = tk.Button(root, text="Update Plot", command=lambda: update_plot(target_freq_slider.get(), mode_area_slider.get()))
    update_button.grid(row=3, column=0, columnspan=2)

    root.mainloop()

if __name__ == '__main__':
    main_gui()
