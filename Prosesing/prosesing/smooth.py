# Python script to plot a heatmap from the given CSV file

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

# Load the CSV file
def load_data(file_path):
    return pd.read_csv(file_path)

# Calculate the mean of the first few frequencies and the difference from the target frequency
def calculate_difference(data, target_freq, num_initial=10):
    first_few_freqs = data.iloc[:, 2:2 + num_initial]
    mean_first_few = first_few_freqs.mean(axis=1)
    difference = data[target_freq] - mean_first_few
    return difference

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
    plt.colorbar(label='Difference (Target - Mean)')
    plt.title(f'Interpolated Heatmap of Signal Difference (Target: {target_freq} MHz)')
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

    # Plot the interpolated heatmap
    plot_heatmap(ra, dec, difference, target_freq)

if __name__ == '__main__':
    main()
