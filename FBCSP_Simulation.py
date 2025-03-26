import os
import numpy as np
import pandas as pd
import mne
from mne.decoding import CSP
import pickle
import argparse

classStandard = {1: 'LeftHand', 2: 'RightHand', 3: 'Jaw', 4: 'LeftHandClench', 5: 'RightHandClench'}

freq_band_names = {
    (1, 4): 'delta',
    (4, 8): 'theta',
    (8, 12): 'alpha',
    (12, 16): 'beta_low',
    (16, 20): 'beta_mid',
    (20, 30): 'beta_high',
    (30, 50): 'gamma'
}

def load_data(file):
    try:
        data = pd.read_csv(file)
        return data
    except FileNotFoundError:
        print(f"Error: File {file} not found.")
        return None
    except Exception as e:
        print(f"An error occurred while loading the file: {e}")
        return None

def transform_and_print(data_file, model_file):
    data_df = load_data(data_file)
    if data_df is None:
        return

    # Define the indices for band power columns and activity column
    band_columns = list(range(56))
    activity_column = -1

    # Extract features and labels from the dataframe
    data = data_df.iloc[:, band_columns].values
    labels = data_df.iloc[:, activity_column].values
    labels = labels.astype(int)

    # Reshape data to (n_segments, n_channels, n_times)
    n_segments = len(data_df)
    n_channels = 8  # There are 8 channels for each frequency band
    n_bands = 7  # There are 7 frequency bands (delta, theta, alpha, beta low, beta mid, beta high, gamma)
    data = data.reshape(n_segments, n_bands, n_channels).transpose(0, 2, 1)  # Shape to (n_segments, n_channels, n_bands)

    # Load the pre-trained CSP models
    with open(model_file, 'rb') as f:
        csp_models = pickle.load(f)

    def update_and_print(segment_idx):
        for freq_band_idx, (fmin, fmax) in enumerate(freq_band_names):
            freq_name = freq_band_names[(fmin, fmax)]
            band_data = data[segment_idx:segment_idx + 1, :, freq_band_idx].reshape(1, n_channels, -1)  # Reshape for CSP

            transformed_data = []

            for class_name in classStandard.values():
                if freq_name in csp_models[class_name]:
                    csp = csp_models[class_name][freq_name]  # Assuming the first CSP model for simplicity
                    transformed = csp.transform(band_data)
                    transformed_data.append(transformed)

            print(f"Segment {segment_idx}, Frequency Band {freq_name} transformed data:\n", transformed_data)

    # Process each segment
    for i in range(n_segments - 1):
        update_and_print(i)

def main():
    parser = argparse.ArgumentParser(description="Transform and print data using trained CSP models.")
    parser.add_argument('--data_file', type=str, required=True, help="Path to the data file.")
    parser.add_argument('--model_file', type=str, required=True, help="Path to the trained CSP model file.")
    args = parser.parse_args()

    transform_and_print(args.data_file, args.model_file)

if __name__ == "__main__":
    main()
