import pandas as pd
import h5py
import numpy as np

def read_csv_data(file_path):
    data_df = pd.read_csv(file_path)
    print("CSV Data (1D Format):")
    print(data_df.head())
    labels = data_df['activity'].values
    transformed_data = data_df.drop(columns=['activity']).values
    return transformed_data, labels

def read_hdf5_data(file_path):
    with h5py.File(file_path, 'r') as f:
        data = f['data'][:]
        labels = f['labels'][:]
    print("HDF5 Data (2D Format):")
    print(f"Data shape: {data.shape}")
    print(f"Labels shape: {labels.shape}")
    return data, labels

def display_2d_structure(data, labels, n_components, freq_band_names, classStandard):
    n_segments, n_bands, n_classes, n_components_per_class = data.shape
    print(f"\nDisplaying structured data for first segment:")
    for band_idx, (fmin, fmax) in enumerate(freq_band_names):
        freq_name = freq_band_names[(fmin, fmax)]
        print(f"\nFrequency Band: {freq_name} ({fmin}-{fmax} Hz)")
        for class_idx, class_name in enumerate(classStandard.values()):
            components = data[0, band_idx, class_idx, :n_components]
            if components is not None and len(components) > 0:
                print(f"  Class: {class_name} - Components: {components}")
            else:
                print(f"  Class: {class_name} - Components: [None]")

def main():
    csv_file_path = './FBCSP/Datasets_FBCSP_4Components/data_konrad/data_konrad_cumulative.csv'
    hdf5_file_path = './FBCSP/Datasets_FBCSP_4Components_2D/data_konrad/data_konrad_cumulative.h5'

    csv_data, csv_labels = read_csv_data(csv_file_path)
    print(f"CSV Transformed Data Shape: {csv_data.shape}")
    print(f"CSV Labels Shape: {csv_labels.shape}")

    hdf5_data, hdf5_labels = read_hdf5_data(hdf5_file_path)
    print(f"HDF5 Transformed Data Shape: {hdf5_data.shape}")
    print(f"HDF5 Labels Shape: {hdf5_labels.shape}")

    freq_band_names = {
        (1, 4): 'delta',
        (4, 8): 'theta',
        (8, 12): 'alpha',
        (12, 16): 'beta_low',
        (16, 20): 'beta_mid',
        (20, 30): 'beta_high',
        (30, 50): 'gamma'
    }

    classStandard = {1: 'LeftHand', 2: 'RightHand', 3: 'Jaw', 4: 'LeftHandClench', 5: 'RightHandClench'}
    
    display_2d_structure(hdf5_data, hdf5_labels, 4, freq_band_names, classStandard)

if __name__ == "__main__":
    main()
