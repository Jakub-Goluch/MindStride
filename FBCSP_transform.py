import os
import numpy as np
import pandas as pd
import mne
from mne.decoding import CSP
import pickle
import argparse
import h5py

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

def transform_data_with_csp(data, labels, csp_models, n_components):
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
                    transformed_segment.append(transformed.flatten()[:n_components])
                else:
                    transformed_segment.append([None] * n_components)
            segment_data.append(transformed_segment)
        transformed_data.append(segment_data)
    
    return np.array(transformed_data)

def save_transformed_data(transformed_data, labels, output_file, freq_band_names, classStandard, n_components, data_format):
    if data_format == '1d':
        # Flatten all components into a single row per segment
        columns = []
        for (fmin, fmax), freq_name in freq_band_names.items():
            for class_name in classStandard.values():
                for comp in range(n_components):
                    columns.append(f'{freq_name}_{class_name}_comp{comp+1}')
        transformed_data_flattened = transformed_data.reshape(transformed_data.shape[0], -1)
        transformed_df = pd.DataFrame(transformed_data_flattened, columns=columns)
        transformed_df['activity'] = labels
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        transformed_df.to_csv(output_file, index=False)
    else:
        # Save data in 2D format using HDF5
        with h5py.File(output_file, 'w') as f:
            f.create_dataset('data', data=transformed_data)
            f.create_dataset('labels', data=labels)
    return transformed_data

def process_and_transform_folder(input_folder, output_folder, model_file, n_components, data_format):
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

                band_columns = list(range(56)) 
                activity_column = -1  

                data = data_df.iloc[:, band_columns].values
                labels = data_df.iloc[:, activity_column].values
                labels = labels.astype(int)

                n_segments = len(data_df)
                n_channels = 8
                n_bands = 7
                data = data.reshape(n_segments, n_bands, n_channels).transpose(0, 2, 1)

                with open(model_file, 'rb') as f:
                    csp_models = pickle.load(f)

                transformed_data = transform_data_with_csp(data, labels, csp_models, n_components)

                relative_path = os.path.relpath(file_path, input_folder)
                output_file_path = os.path.join(output_folder, relative_path).replace('.csv', f'.{"h5" if data_format == "3d" else "csv"}')
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                save_transformed_data(transformed_data, labels, output_file_path, freq_band_names, classStandard, n_components, data_format)
                print(f"Transformed data saved to: {output_file_path}")

                user_folder = os.path.basename(os.path.dirname(os.path.dirname(relative_path)))
                if user_folder not in user_data_map:
                    user_data_map[user_folder] = []
                user_data_map[user_folder].append((transformed_data, labels))

                cumulative_data_all.append((transformed_data, labels))

    for user, data_frames in user_data_map.items():
        user_cumulative_data = np.concatenate([data for data, _ in data_frames], axis=0)
        user_cumulative_labels = np.concatenate([labels for _, labels in data_frames], axis=0)
        user_cumulative_file = os.path.join(output_folder, user, f'{user}_cumulative.{"h5" if data_format == "3d" else "csv"}')
        os.makedirs(os.path.dirname(user_cumulative_file), exist_ok=True)
        save_transformed_data(user_cumulative_data, user_cumulative_labels, user_cumulative_file, freq_band_names, classStandard, n_components, data_format)
        print(f"Cumulative data saved for user {user} to: {user_cumulative_file}")

    if cumulative_data_all:
        cumulative_data = np.concatenate([data for data, _ in cumulative_data_all], axis=0)
        cumulative_labels = np.concatenate([labels for _, labels in cumulative_data_all], axis=0)
        cumulative_file_all = os.path.join(output_folder, f'cumulative_all_users.{"h5" if data_format == "3d" else "csv"}')
        save_transformed_data(cumulative_data, cumulative_labels, cumulative_file_all, freq_band_names, classStandard, n_components, data_format)
        print(f"Cumulative data for all users saved to: {cumulative_file_all}")

def main():
    parser = argparse.ArgumentParser(description="Transform data using trained CSP models and save the transformed data.")
    parser.add_argument('--input_dir', type=str, required=True, help="Path to the input data directory.")
    parser.add_argument('--output_dir', type=str, required=True, help="Path to the output data directory.")
    parser.add_argument('--model_file', type=str, required=True, help="Path to the trained CSP model file.")
    parser.add_argument('--n_components', type=int, default=4, help="Number of CSP components to use.")
    parser.add_argument('--data_format', type=str, choices=['1d', '3d'], default='1d', help="Format of the output data: '1d' for one-dimensional vector or '3d' for three-dimensional vector.")
    args = parser.parse_args()

    process_and_transform_folder(args.input_dir, args.output_dir, args.model_file, args.n_components, args.data_format)

if __name__ == "__main__":
    main()
