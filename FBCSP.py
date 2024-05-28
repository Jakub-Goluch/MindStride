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

def train_csp_models(data, labels, freq_bands, class_standard, update_existing=False, model_file=None):
    classes = list(class_standard.values())
    
    if update_existing and model_file:
        try:
            with open(model_file, 'rb') as f:
                csp_models = pickle.load(f)
            print("Loaded existing CSP models.")
        except FileNotFoundError:
            print(f"Model file {model_file} not found. Training new models.")
            csp_models = {class_name: {freq_name: None for freq_name in freq_band_names.values()} for class_name in classes}
    else:
        csp_models = {class_name: {freq_name: None for freq_name in freq_band_names.values()} for class_name in classes}

    for class_idx, class_name in class_standard.items():
        binary_labels = (labels == class_idx).astype(int)  # One-vs-rest labels
        print(f"Training CSP for class {class_name} with binary labels: {np.unique(binary_labels, return_counts=True)}")
        print(f"Binary labels for class {class_name}: {binary_labels[:10]}")  

        for band_idx, (fmin, fmax) in enumerate(freq_bands):
            freq_name = freq_band_names[(fmin, fmax)]
            if csp_models[class_name][freq_name] is None:
                csp_models[class_name][freq_name] = CSP(n_components=2, reg=None, log=True, norm_trace=False)
            try:
                csp_models[class_name][freq_name].fit(data, binary_labels)
                print(f"Updated CSP for class {class_name}, frequency band {freq_name} ({fmin}-{fmax} Hz)")
            except ValueError as e:
                print(f"Error training CSP for class {class_name}, frequency band {freq_name} ({fmin}-{fmax} Hz): {e}")

    return csp_models

def process_folder(folder_path, model_file, update_existing):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")

                data_df = load_data(file_path)
                if data_df is None:
                    continue

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

                freq_bands = [(1, 4), (4, 8), (8, 12), (12, 16), (16, 20), (20, 30), (30, 50)]

                csp_models = train_csp_models(data, labels, freq_bands, classStandard, update_existing, model_file)
                
                # Save the trained CSP models for real-time use
                with open(model_file, 'wb') as f:
                    pickle.dump(csp_models, f)
                print(f"CSP models saved to {model_file}")

def main():
    parser = argparse.ArgumentParser(description="Train or update CSP models for each dataset in a directory.")
    parser.add_argument('--data_dir', type=str, required=True, help="Path to the data directory.")
    parser.add_argument('--model_file', type=str, help="Path to save/load CSP models.")
    parser.add_argument('--update_existing', action='store_true', help="Flag to update existing models.")
    args = parser.parse_args()

    process_folder(args.data_dir, args.model_file, args.update_existing)

if __name__ == "__main__":
    main()
