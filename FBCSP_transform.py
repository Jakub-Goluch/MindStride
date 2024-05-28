import os
import numpy as np
import pandas as pd
import pickle
from mne.decoding import CSP
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

def transform_data_with_csp(data, labels, csp_models):
    transformed_data = []

    for segment_idx in range(data.shape[0]):
        segment_data = []
        for freq_band_idx, (fmin, fmax) in enumerate(freq_band_names):
            freq_name = freq_band_names[(fmin, fmax)]
            band_data = data[segment_idx, :, freq_band_idx].reshape(1, data.shape[1], -1)  # Reshape for CSP

            transformed_segment = []
            for class_name in classStandard.values():
                if freq_name in csp_models[class_name]:
                    csp = csp_models[class_name][freq_name]
                    transformed = csp.transform(band_data)
                    transformed_segment.extend(transformed.flatten())
            segment_data.append(transformed_segment)
        transformed_data.append(segment_data)
    
    return np.array(transformed_data)

def save_transformed_data(transformed_data, labels, output_file, freq_band_names, classStandard):
    columns = []
    for (fmin, fmax), freq_name in freq_band_names.items():
        for class_name in classStandard.values():
            for comp in range(2):  # Only 2 CSP components
                columns.append(f'{freq_name}_{class_name}_comp{comp+1}')

    transformed_df = pd.DataFrame(transformed_data.reshape(transformed_data.shape[0], -1), columns=columns)
    transformed_df['activity'] = labels
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    transformed_df.to_csv(output_file, index=False)
    return transformed_df

def process_and_transform_folder(input_folder, output_folder, model_file):
    cumulative_data_all = []
    user_data_map = {}

    for root, dirs, files in os.walk(input_folder):
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

                # Load the pre-trained CSP models
                with open(model_file, 'rb') as f:
                    csp_models = pickle.load(f)

                # Transform data using CSP models
                transformed_data = transform_data_with_csp(data, labels, csp_models)

                # Save transformed data
                relative_path = os.path.relpath(file_path, input_folder)
                output_file_path = os.path.join(output_folder, relative_path)  # Ensure current directory
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                transformed_df = save_transformed_data(transformed_data, labels, output_file_path, freq_band_names, classStandard)
                print(f"Transformed data saved to: {output_file_path}")

                # Collect cumulative data for the user
                user_folder = os.path.basename(os.path.dirname(os.path.dirname(relative_path)))
                if user_folder not in user_data_map:
                    user_data_map[user_folder] = []
                user_data_map[user_folder].append(transformed_df)

                # Collect cumulative data for all users
                cumulative_data_all.append(transformed_df)

    # Save cumulative data for each user
    for user, data_frames in user_data_map.items():
        user_cumulative_df = pd.concat(data_frames, ignore_index=True)
        user_cumulative_file = os.path.join(output_folder, user, f'{user}_cumulative.csv')
        os.makedirs(os.path.dirname(user_cumulative_file), exist_ok=True)
        user_cumulative_df.to_csv(user_cumulative_file, index=False)
        print(f"Cumulative data saved for user {user} to: {user_cumulative_file}")

    # Save cumulative data for all users
    if cumulative_data_all:
        cumulative_df_all = pd.concat(cumulative_data_all, ignore_index=True)
        cumulative_file_all = os.path.join(output_folder, 'cumulative_all_users.csv')
        cumulative_df_all.to_csv(cumulative_file_all, index=False)
        print(f"Cumulative data for all users saved to: {cumulative_file_all}")

def main():
    parser = argparse.ArgumentParser(description="Transform data using trained CSP models and save the transformed data.")
    parser.add_argument('--input_dir', type=str, required=True, help="Path to the input data directory.")
    parser.add_argument('--output_dir', type=str, required=True, help="Path to the output data directory.")
    parser.add_argument('--model_file', type=str, required=True, help="Path to the trained CSP model file.")
    args = parser.parse_args()

    process_and_transform_folder(args.input_dir, args.output_dir, args.model_file)

if __name__ == "__main__":
    main()
