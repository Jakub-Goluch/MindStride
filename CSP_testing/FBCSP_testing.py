import numpy as np
import mne
from mne.decoding import CSP
import pickle

def load_data(file):
    try:
        with open(file, 'r') as f:
            data = f.read()
        return data
    except FileNotFoundError:
        print(f"Error: File {file} not found.")
        return None
    except Exception as e:
        print(f"An error occurred while loading the file: {e}")
        return None

# Load the data
data_str = load_data('MindStride/CSP_testing/Sianuga_1-1.csv')
if data_str is None:
    raise SystemExit("Data loading failed. Exiting.")

# Parse data into a numpy array
data_lines = data_str.strip().split("\n")
data = np.array([list(map(float, line.split(','))) for line in data_lines])

# Parameters
update_rate = 25  # 25 Hz update rate
segment_duration = 1  # 1 second segments
samples_per_segment = update_rate * segment_duration

# Define frequency bands based on your device
freq_bands = [(1, 4), (4, 8), (12, 16), (16, 20), (20, 30), (30, 50)]

# Divide data into 1-second segments
n_samples, n_features = data.shape
n_segments = n_samples // samples_per_segment

# Ensure the data array can be divided into complete segments
data = data[:n_segments * samples_per_segment]

# Reshape data to (n_segments, samples_per_segment, n_features)
data_reshaped = data.reshape(n_segments, samples_per_segment, n_features)

n_channels = 8

# Create labels for each of the 5 classes
classes = ['LeftHand', 'RightHand', 'Jaw', 'LeftHandClench', 'RightHandClench']
labels = np.array([i % 5 for i in range(n_segments)])


data_csp = [
    np.random.randn(n_segments, samples_per_segment, n_features) for _ in freq_bands
]


csp_models = {class_name: [] for class_name in classes}

# Train CSP filters for each frequency band and each class (one-vs-rest)
for class_idx, class_name in enumerate(classes):
    binary_labels = (labels == class_idx).astype(int)  # One-vs-rest labels
    for band_idx, band_data in enumerate(data_csp):

        csp = CSP(n_components=2, reg=None, log=True, norm_trace=False)

        csp.fit(band_data, binary_labels)

        csp_models[class_name].append(csp)
        print(f"Trained CSP for class {class_name}, frequency band {freq_bands[band_idx][0]}-{freq_bands[band_idx][1]} Hz")

# Save the trained CSP models for real-time use
with open('MindStride/CSP_testing/trained_csp_models.pkl', 'wb') as f:
    pickle.dump(csp_models, f)