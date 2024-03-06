import pandas as pd
import os

###drop duplicates frame_no
###add missing frame_no
# normalizing X,Y Values


import pandas as pd
import os


def normalize_data(df):
    # Normalize X and Y columns
    df['X'] = (df['X'] - df['X'].min()) / (df['X'].max() - df['X'].min())
    df['Y'] = (df['Y'] - df['Y'].min()) / (df['Y'].max() - df['Y'].min())
    return df


def process_data(folder_path):
    for folder_num in range(1, 49):
        folder_name = f'{folder_num:02d}'
        folder_dir = os.path.join(folder_path, folder_name)

        for video_num in range(9):
            csv_filename = f'video_{video_num}-projection.csv'
            csv_path = os.path.join(folder_dir, csv_filename)

            if os.path.exists(csv_path):
                # Read CSV file into DataFrame
                df = pd.read_csv(csv_path)

                # Drop frame 0 row if it exists
                if 'Frame.No' in df.columns:
                    df = df[df['Frame.No'] != 0]

                # Drop duplicates based on Frame.No column
                df.drop_duplicates(subset=['Frame.No'], inplace=True)

                # Ensure Frame.No values are consecutive
                df['Frame.No'] = range(1, len(df) + 1)

                # Fill missing values by duplicating previous row
                df = df.set_index('Frame.No').reindex(range(1, len(df) + 1), method='ffill')

                # Normalize X and Y columns
                df = normalize_data(df)

                # Save the new dataframe
                new_csv_filename = f'video_{video_num}-projection-pre.csv'
                print(new_csv_filename)
                new_csv_path = os.path.join(folder_dir, new_csv_filename)
                df.to_csv(new_csv_path)


# Example usage:
process_data('.')
