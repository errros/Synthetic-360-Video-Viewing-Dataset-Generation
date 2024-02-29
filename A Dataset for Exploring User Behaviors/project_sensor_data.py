import cv2
import pandas as pd
import numpy as np
import os
import re
from sensor_projection_utils import *

# project sensor data for each user on each video and save csv files of projected X,Y , X_pixel , Y_pixel values

def process_videos_and_csvs(saliency_dir, experiment_dir):
    # List all .avi files in the saliency directory
    saliency_videos = [f for f in os.listdir(saliency_dir) if f.endswith('-sal.avi')]

    # Directories to exclude
    exclude_dirs = {'saliency'}

    # Iterate over each saliency video
    for video_name in saliency_videos:
        # Extract the numerical part and convert to int
        video_number = int(re.search(r'(\d+)-sal\.avi', video_name).group(1))

        # Iterate over subdirectories in the experiment directory, excluding 'saliency'
        for subdir in os.listdir(experiment_dir):
            subdir_path = os.path.join(experiment_dir, subdir)
            if os.path.isdir(subdir_path) and subdir not in exclude_dirs:
                csv_path = os.path.join(subdir_path, f'video_{video_number-1}.csv')
                if os.path.exists(csv_path):
                    df_user = pd.read_csv(csv_path)
                    df_user = df_user[df_user.index % 2 == 0]

                    # Assume video_path is defined or found similarly to csv_path
                    video_path = os.path.join(saliency_dir, video_name)
                    video = cv2.VideoCapture(video_path)
                    frame_rate = video.get(cv2.CAP_PROP_FPS)
                    resolution = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))

                    # Initialize an empty DataFrame for trajectory data
                    trajectory_df = pd.DataFrame(columns=['Timestamp', 'Frame.No', 'X', 'Y', 'X_pixel', 'Y_pixel'])
                    new_rows = []  # List to store new rows before concatenation
                    for index, row in df_user.iterrows():
                        playback_time = row['PlaybackTime']
                        target_frame_number = int(playback_time * frame_rate)

                        q = [row['UnitQuaternion.w'], row['UnitQuaternion.x'], row['UnitQuaternion.y'],
                             row['UnitQuaternion.z']]
                        direction_vect = direction_vect_from_quaternion_in_cartesian(q)
                        direction_vect_spherical = vect_cartesian_to_spherical(direction_vect)
                        equirect_point_cartesian = project_spherical_vect_to_equirect_point(direction_vect_spherical)
                        x_pixel, y_pixel = equirect_point_to_pixels(equirect_point_cartesian, resolution)
                        # Prepare new row as a DataFrame to enable concat
                        new_row = pd.DataFrame({
                            'Timestamp': [playback_time],
                            'Frame.No': target_frame_number,
                            'X': [equirect_point_cartesian[0]],
                            'Y': [equirect_point_cartesian[1]],
                            'X_pixel': [x_pixel],
                            'Y_pixel': [y_pixel]
                        })

                        user_no = subdir_path.split('/')[-1]
                        if target_frame_number % 100 == 0:
                            print(f'Video No : {video_number} , User : {user_no} , Frame : {target_frame_number}')
                        new_rows.append(new_row)

                    # Concatenate all new rows at once
                    if new_rows:  # Check if there are any rows to add
                        trajectory_df = pd.concat([trajectory_df] + new_rows, ignore_index=True)
                        # Save the modified DataFrame
                    output_csv_path = csv_path.replace('.csv', '-projection.csv')
                    trajectory_df.to_csv(output_csv_path, index=False)
                    print(f"Saved processed data to {output_csv_path}")

                    video.release()


saliency_dir = './saliency'
experiment_dir = '.'
process_videos_and_csvs(saliency_dir, experiment_dir)