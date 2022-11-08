import pandas as pd
import math
import numpy as np
import tqdm
import os
from pathlib import Path

def read_DLC_data(dlc_file_path):
        
    # read hdf file which is produced from DeepLabCut (DLC).
    dlc_hdf = pd.read_hdf(dlc_file_path)

    # create a dictionary which holds some information about the DLC hdf file
    # Keyes: level names: e.g. scorer , individuals, keypoints, coords
    # Values: lavel values: e.g. DLC project name (as scorer), mouse1, snout, x
    dlc_hdf_info = {}

    # length of tge level of the DLC hdf file (=4)
    lvl_depth = len(dlc_hdf.columns.levels)

    # assign values to the `dlc_hdf_info` dictionary. See the dictionary decleration description for more information
    for i in range(0, lvl_depth):
        dlc_hdf_lvl_name = dlc_hdf.columns.levels[i].name
        dlc_hdf_col_name = dlc_hdf.columns.levels[i]
        dlc_hdf_info[dlc_hdf_lvl_name] = dlc_hdf_col_name
        
    # get the number of mice in the dlc hdf file
    # dlc_nr_mice = len(dlc_hdf_info['individuals'])
    
    return dlc_hdf, dlc_hdf_info

# def filter_threshold_DLC_data(DLC_hdf, dlc_hdf_info):
#         # filter detections with likelihood less than 0.9
#     filtered_dlc_hdf = DLC_hdf.copy()
#     print(DLC_hdf)
#     dlc_hdf_size = len(filtered_dlc_hdf.index)
#     pbar = tqdm.tqdm(total=dlc_hdf_size, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
#     for i in range(dlc_hdf_size):
#         for mouse in dlc_hdf_info['individuals']:
#             for bp in dlc_hdf_info['bodyparts']:
#                 if filtered_dlc_hdf.loc[i, (dlc_hdf_info['scorer'][0], mouse, bp, 'likelihood')] <= 0.9:
#                     filtered_dlc_hdf.loc[i, (dlc_hdf_info['scorer'][0], mouse, bp, 'x')] = math.nan
#                     filtered_dlc_hdf.loc[i, (dlc_hdf_info['scorer'][0], mouse, bp, 'y')] = math.nan
#         pbar.update(1)

#     pbar.close()

#     print(filtered_dlc_hdf)
#     return filtered_dlc_hdf    
    

def save_DLC_hdf(hdf_file, output_directory, dlc_file_name, detailed_name):
    
    Path(os.path.join(output_directory, "tracks_results")).mkdir(parents=True, exist_ok=True)
    
    filename = f'{dlc_file_name}_{detailed_name}.h5'
    
    hdf_file.to_hdf(os.path.join(output_directory, 'tracks_results', filename), "df", mode='w',format='table')



# def calc_RFID_pos(RFID_df_coords, row):
#     x, y = row.x, row.y
#     for i in range(len(RFID_df_coords)):
#         area_coords = RFID_df_coords.area_coords.loc[i]        
#         RFID_reader = RFID_df_coords.RFID_reader.loc[i] 
       
#         if (x > area_coords[0][0] and
#             y > area_coords[0][1] and 
#             x < area_coords[1][0] and 
#             y < area_coords[1][1]):

#             return RFID_reader


def create_DLC_centroid(dlc_hdf, dlc_hdf_info, likelihood_threshold):
    print('Processing centroid of DLC mice bodyparts..')
    pbar = tqdm.tqdm(total = len(dlc_hdf), bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')

    individuals = dlc_hdf_info['individuals']
    bodyparts = dlc_hdf_info['bodyparts']
    scorer = dlc_hdf_info['scorer'][0]
    crucial_bp = ['shoulder', 'spine1', 'spine2', 'spine3', 'spine4']

    # frames = []
    # mice_id = []
    # x_list = []
    # y_list = []
    # nr_mice_hdf = (2 * len(individuals))

    arr = np.zeros(shape=(len(dlc_hdf), 2 * len(individuals)))    

    for frame in range(len(dlc_hdf)-1):
        
        mice_coords = []
        
        for mouse in individuals:
            
            centroid_x = math.nan
            centroid_y = math.nan
            count_centroid = 0
            
            for bodypart in bodyparts:
                x = dlc_hdf[scorer, mouse, bodypart, 'x'].iloc[frame]
                y = dlc_hdf[scorer, mouse, bodypart, 'y'].iloc[frame]
                likelihood = dlc_hdf[scorer, mouse, bodypart, 'likelihood'].iloc[frame]
                if bodypart in crucial_bp:
                    # calc centroid coords
                    if not (math.isnan(x) or math.isnan(y)) and likelihood >= likelihood_threshold:
                        centroid_x = np.nansum([centroid_x, x]) # np.nansum(.)
                        centroid_y = np.nansum([centroid_y, y])
                        count_centroid += 1

            if not (math.isnan(centroid_x) or math.isnan(centroid_x)):
                # calc mean of coords of bodyparts
                centroid_x /= count_centroid
                centroid_y /= count_centroid

            # collect all coords of a particular    
            mice_coords.append(centroid_x)
            mice_coords.append(centroid_y)
            # frames.append(frame+1)
            # mice_id.append(mouse)
            # x_list.append(centroid_x)
            # y_list.append(centroid_y)
        
        # add a row of all mice coords of the same frame
        arr[frame] = mice_coords

        pbar.update(1)

    iterables = [individuals, ["x", "y"]]
    index = pd.MultiIndex.from_product(iterables, names=["individuals", "coords"])

    DLC_hdf_centroid = pd.DataFrame(arr, index=dlc_hdf.index+1, columns=index)

    # DLC_df_centroid = pd.DataFrame(list(zip(frames, mice_id, x_list, y_list)), columns=['Frame', 'Mouse_ID', 'x', 'y'])
    pbar.close()

    return DLC_hdf_centroid