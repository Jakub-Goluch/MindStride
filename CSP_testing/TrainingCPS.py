import numpy as np
from mne.decoding import CSP
import mne

def load_data(file):
    with open(file, 'r') as f:
        data = f.read()
    return data

# Load the data
data_str = load_data('MindStride/CSP_testing/Sianuga_1-1.csv')

# Parse data into a numpy array
data_lines = data_str.strip().split("\n")
data = np.array([list(map(float, line.split(','))) for line in data_lines])

# Parameters
update_rate = 25  # 25 Hz update rate
segment_duration = 1  # 1 second segments
samples_per_segment = update_rate * segment_duration

# Divide data into 1-second segments
n_samples, n_features = data.shape
n_segments = n_samples // samples_per_segment

# Ensure the data array can be divided into complete segments
data = data[:n_segments * samples_per_segment]

# Reshape data to (n_segments, samples_per_segment, n_features)
data_reshaped = data.reshape(n_segments, samples_per_segment, n_features)

n_channels = 8
n_freq_bands = 7

# Extract relevant data for CSP (channels x frequency bands)
data_csp = data_reshaped[:, :, :n_channels * n_freq_bands]

# Create labels for CSP 
# Create labels for each of the 5 classes
classes = ['LeftHand', 'RightHand', 'Jaw', 'LeftHandClench', 'RightHandClench']
labels = np.array([i % 5 for i in range(n_segments)])

# Initialize CSP
csp_components = 2
csp = CSP(n_components=csp_components, reg=None, log=True, norm_trace=False)

# Train CSP filters offline using all data
csp_patterns = []
for freq_band in range(n_freq_bands):
    band_data = data_csp[:, :, freq_band * n_channels:(freq_band + 1) * n_channels]
    csp.fit(band_data, labels)
    csp_patterns.append(csp.patterns_[:n_channels, :csp_components])

# Save the trained CSP model for real-time use
import pickle
with open('MindStride/CSP_testing/trained_csp.pkl', 'wb') as f:
    pickle.dump(csp, f)
