import os
import json
import pandas as pd
import argparse

classStandard = {1: 'LeftHand', 2: 'RightHand', 3: 'Jaw', 4: 'LeftHandClench', 5: 'RightHandClench'}

video_to_class = {
    "Left-2s.mp4": "LeftHand",
    "Right-2s.mp4": "RightHand",
    "Jaw-2s.mp4": "Jaw",
    "Left_Squeeze-2s.mp4": "LeftHandClench",
    "Right_Squeeze-2s.mp4": "RightHandClench"
}

def load_csv(file):
    try:
        data = pd.read_csv(file)
        return data
    except FileNotFoundError:
        print(f"Error: File {file} not found.")
        return None
    except Exception as e:
        print(f"An error occurred while loading the file: {e}")
        return None

def load_history_labels(file):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File {file} not found.")
        return None
    except Exception as e:
        print(f"An error occurred while loading the file: {e}")
        return None

def create_label_mapping(history_labels, video_to_class, class_standard):
    label_mapping = {}
    for idx, (video, count) in enumerate(history_labels.items(), start=1):
        if video in video_to_class:
            standard_label = video_to_class[video]
            for key, value in class_standard.items():
                if value == standard_label:
                    label_mapping[idx] = key
                    break
    print(f"Created label mapping: {label_mapping}")
    return label_mapping

def update_csv_labels(csv_data, label_mapping):
    activity_column = csv_data.columns[-1]
    print(f"Updating column '{activity_column}' with mapping {label_mapping}")
    
    for index, row in csv_data.iterrows():
        value = row[activity_column]
        if isinstance(value, str):
            if value.startswith('[') and value.endswith(']'):
                value = value[-2]
        original_value = int(value)
        if original_value == 0:
            continue
        else:
            mapped_value = label_mapping[original_value]
            csv_data.at[index, activity_column] = mapped_value

    return csv_data

def process_folder(folder_path, video_to_class, class_standard):
    for root, dirs, files in os.walk(folder_path):
        json_file = None
        for file in files:
            if file.endswith('.json'):
                json_file = os.path.join(root, file)
                break
        
        if not json_file:
            print(f"No JSON file found in {root}. Skipping folder.")
            continue
        
        history_labels = load_history_labels(json_file)
        if not history_labels:
            print(f"Failed to load JSON file: {json_file}. Skipping folder.")
            continue
        
        label_mapping = create_label_mapping(history_labels, video_to_class, class_standard)

        for file in files:
            if file.endswith('.csv'):
                csv_file_path = os.path.join(root, file)
                csv_data = load_csv(csv_file_path)
                if csv_data is not None:
                    updated_csv_data = update_csv_labels(csv_data, label_mapping)
                    updated_csv_data.to_csv(csv_file_path, index=False)
                    print(f"Updated CSV file: {csv_file_path}")
                        

def main():
    parser = argparse.ArgumentParser(description="Update CSV files with standardized labels based on JSON history files.")
    parser.add_argument('--data_dir', type=str, required=True, help="Path to the data directory.")
    args = parser.parse_args()

    process_folder(args.data_dir, video_to_class, classStandard)

if __name__ == "__main__":
    main()
