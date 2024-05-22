import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
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

# Load the standard montage
montage = mne.channels.make_standard_montage('standard_1020')

# Extract positions for the 8 electrodes
electrode_names = ['Fz', 'C3', 'Cz', 'C4', 'Pz', 'PO7', 'Oz', 'PO8']
pos_dict = montage.get_positions()['ch_pos']
pos = np.array([pos_dict[name] for name in electrode_names])
pos_2d = pos[:, :2]

# Interactive plot of CSP patterns
fig, axes = plt.subplots(n_freq_bands, csp_components, figsize=(15, 10))
plt.subplots_adjust(bottom=0.25)

def plot_csp_patterns(csp_patterns):
    for freq_band in range(n_freq_bands):
        for comp in range(csp_components):
            ax = axes[freq_band, comp]
            ax.clear()
            pattern = csp_patterns[freq_band][:, comp]
            mne.viz.plot_topomap(pattern, pos=pos_2d, axes=ax, show=False)
            ax.set_title(f'Band {freq_band + 1} CSP Component {comp + 1}')
            for idx, name in enumerate(electrode_names):
                ax.annotate(name, xy=pos_2d[idx], xytext=(5, 5), textcoords='offset points', fontsize=9, color='black')

# Plot the initial CSP patterns
plot_csp_patterns(csp_patterns)

# Interactive slider for visualizing the real-time CSP application
ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
time_slider = Slider(ax_slider, 'Time', 0, n_segments - 1, valinit=0, valstep=1)

def update(val):
    segment_idx = int(time_slider.val)
    new_patterns = []
    for freq_band in range(n_freq_bands):
        band_data = data_csp[segment_idx:segment_idx+1, :, freq_band * n_channels:(freq_band + 1) * n_channels]
        transformed_data = csp.transform(band_data) 

        new_patterns.append(csp.patterns_[:n_channels, :csp_components]) 
    plot_csp_patterns(new_patterns)
    fig.canvas.draw_idle()

time_slider.on_changed(update)

plt.show()
