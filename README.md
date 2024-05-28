
# README

## Files and Their Descriptions

### FBCSP.py

This script is used for training or updating CSP models for each dataset in a directory.

#### How to Use:
```bash
python FBCSP.py --data_dir <path_to_data_directory> --model_file <path_to_save_or_load_model> [--update_existing]
```
- `--data_dir`: Path to the directory containing the input CSV files.
- `--model_file`: Path to save or load the CSP models.
- `--update_existing`: (Optional) Flag to update existing models if they exist.

### FBCSP_Simulation.py

This script is used for transforming and printing the data using trained CSP models. It is useful for verifying the transformation process and inspecting the transformed data.

#### How to Use:
```bash
python FBCSP_Simulation.py --data_file <path_to_data_file> --model_file <path_to_trained_model>
```
- `--data_file`: Path to the input CSV file.
- `--model_file`: Path to the trained CSP model file.


### FBCSP_transform.py

This script transforms the data using trained CSP models and saves the transformed data into a specified output directory. It also creates cumulative files for each user and one for all users.

#### How to Use:
```bash
python FBCSP_transform.py --input_dir <path_to_input_directory> --output_dir <path_to_output_directory> --model_file <path_to_trained_model>
```
- `--input_dir`: Path to the directory containing the input CSV files.
- `--output_dir`: Path to the directory where the transformed CSV files will be saved.
- `--model_file`: Path to the trained CSP model file.

## Final CSP CSV Format

The final CSP-transformed CSV files have the following structure:
- Each row corresponds to a data segment.
- Columns are named according to the frequency band, class, and CSP component, e.g., `delta_LeftHand_comp1`, `theta_RightHand_comp2`, etc.
- The last column is `activity`, which contains the class label for each segment.

## Folder Structure

### Input Data Folder (Example)

```
<MainFolder>
│
└───<User1>
│   │
│   └───<User1_Day1>
│   │   │   file1.csv
│   │   │   file2.csv
│   │
│   └───<User1_Day2>
│       │   file1.csv
│       │   file2.csv
│
└───<User2>
    │
    └───<User2_Day1>
    │   │   file1.csv
    │   │   file2.csv
    │
    └───<User2_Day2>
        │   file1.csv
        │   file2.csv
```

### Output Data Folder (Example)

```
<OutputFolder>
│
└───<User1>
│   │   User1_cumulative.csv
│   │
│   └───<User1_Day1>
│   │   │   file1.csv
│   │   │   file2.csv
│   │
│   └───<User1_Day2>
│       │   file1.csv
│       │   file2.csv
│
└───<User2>
    │   User2_cumulative.csv
    │
    └───<User2_Day1>
    │   │   file1.csv
    │   │   file2.csv
    │
    └───<User2_Day2>
        │   file1.csv
        │   file2.csv
```

### Cumulative Files

- `<OutputFolder>/User1/User1_cumulative.csv`: Cumulative data for User1 across all days.
- `<OutputFolder>/User2/User2_cumulative.csv`: Cumulative data for User2 across all days.
- `<OutputFolder>/cumulative_all_users.csv`: Cumulative data for all users.


## Structure of Transformed CSP CSV Data

The transformed CSP CSV data contains columns representing the CSP components for each frequency band and each class, followed by an 'activity' column which holds the labels. The column names are structured as follows:


### Column Details

- **Frequency Bands:** The data includes CSP components for 7 frequency bands: delta, theta, alpha, beta_low, beta_mid, beta_high, and gamma.
- **Classes:** Each frequency band has CSP components for 5 classes: LeftHand, RightHand, Jaw, LeftHandClench, and RightHandClench.
- **Components:** Each class has 2 CSP components: comp1 and comp2.
- **Activity:** The last column is 'activity', which holds the labels for the data segments.

### Total Number of Columns

The total number of columns is calculated as follows:
- Frequency bands: 7
- Classes per frequency band: 5
- Components per class: 2
- Plus 1 activity column


This results in a total of 71 columns in the transformed CSP CSV data.
