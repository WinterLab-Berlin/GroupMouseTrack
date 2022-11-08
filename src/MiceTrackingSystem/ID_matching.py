# from pandas import value_counts

from RFID import *
from DLC import *
import itertools


# Process data
def process_RFID(input_video_path, output_directory, video_name, RFID_file_path, ts_start, duration, fps, height, width, TIME_WINDOW_LENGTH, RFID_reader_names, method, img_path=None):
    
    # Clean and process RFID data
    RFID_df = read_RFID_data(RFID_file_path)
    RFID_df_coords = extract_RFID_coords(RFID_df)
    RFID_df, RFID_df_coords = clean_RFID_data(RFID_df, RFID_df_coords)
    RFID_df = shift_RFID_date(RFID_df)
    RFID_df, ts_start = cut_RFID_data(RFID_df, ts_start, duration)
    RFID_df = add_frame_to_RFID(RFID_df, ts_start, fps)
    RFID_df_coords = scale_RFID_coords_manually(RFID_df_coords) # not used anymore!
    # RFID_df_coords = pick_RFID_reader_pos(RFID_reader_names, method, RFID_df_coords, input_video_path, img_path)

    add_RFID_area(RFID_df_coords, height, width) # inplace because of apply!

    # process
    # RFID_df_full_mean = create_full_mean_df_RFID_in_time_window(RFID_df_coords, RFID_df, ts_start, fps,TIME_WINDOW_LENGTH)
    RFID_df_mean = create_mean_df_RFID_in_time_window(RFID_df_coords, RFID_df, ts_start, fps,TIME_WINDOW_LENGTH)
    
    return RFID_df_coords, RFID_df_mean

def process_DLC(dlc_file_path, likelihood_threshold):
    
    DLC_hdf, dlc_hdf_info = read_DLC_data(dlc_file_path)
    DLC_hdf_centroid = create_DLC_centroid(DLC_hdf, dlc_hdf_info, likelihood_threshold)
    return DLC_hdf_centroid, DLC_hdf, (dlc_hdf_info)

def match_id(RFID_df_coords, RFID_df_mean, dlc_hdf_info, DLC_hdf, DLC_hdf_centroid, TIME_WINDOW_LENGTH, fps, output_directory):

    scorer = dlc_hdf_info['scorer'][0]
    DLC_mice_id = dlc_hdf_info['individuals']
    bodyparts = dlc_hdf_info['bodyparts']
    RFID_mice_id = RFID_df_mean['Mouse_ID'].unique()
 
    DLC_RFID_overlap_dict = find_all_overlaps(RFID_df_coords, RFID_df_mean, DLC_hdf_centroid, TIME_WINDOW_LENGTH, fps)
    with open(os.path.join(output_directory, 'overlap_{}s.txt'.format(TIME_WINDOW_LENGTH)), 'w') as f:
        print(DLC_RFID_overlap_dict, file=f)
        # f.write(DLC_RFID_overlap_dict)
    
    # match and assign ID
    matching_reference = find_id_match(RFID_mice_id, DLC_mice_id, DLC_RFID_overlap_dict)
    DLC_hdf, DLC_hdf_centroid = assign_RFID_id_to_DLC(DLC_hdf, DLC_hdf_centroid, matching_reference)

    return DLC_hdf, DLC_hdf_centroid


# Read data
def get_files_paths(files_dir=None):
    
    if files_dir is None:
        msg ='Enter the path of a directory which contains a: \ncsv file for RFID-data, \na video of mice and \na file containig the starting timestamp of the video: \n'
        input_files_directory = input(msg)
    else:
        input_files_directory = files_dir
        
    print(f'files directory: {input_files_directory}')

    for _, _, files in os.walk(input_files_directory):
        for filename in files:
            if filename.endswith('Thermo.csv'):
                RFID_file_path= os.path.join(input_files_directory, filename)
                print(RFID_file_path)

            # load original (mp4) video
            elif filename.endswith('.mp4') or filename.endswith('.H264'):
                input_video_path= os.path.join(input_files_directory, filename)
                print(input_video_path)

            # load DLC labeled video
            # if filename.endswith('id_labeled.mp4'):
            #     input_video_path_dlc_id_labeled = os.path.join(input_files_directory, filename)
            #     print(input_video_path_dlc_id_labeled)

            elif filename.endswith('start_ts.txt'):
                file_start_ts = os.path.join(input_files_directory, filename)
                print(file_start_ts)
                
            elif filename.endswith('.h5'):
                dlc_file_name = filename
                dlc_file_path = os.path.join(input_files_directory, filename)

    # dlc_file_name = os.path.basename(os.path.splitext(dlc_file_path)[0])
    
    return input_files_directory, input_video_path, file_start_ts, dlc_file_path, dlc_file_name, RFID_file_path 

def get_video_info(input_video_path, input_files_directory, file_start_ts, output_directory = None):
    # Prepare for reading video
    # input_video_path = r"X:\Social-Interaction\Tracking\test_with_hand_transponder_and_piCam\recording_RP_2022-05-18@20_57_52f309430.mp4"
    # print(f'input_video_path: {input_video_path}')

    video_name = input_video_path.split('\\')[-1].split('.')[0]
    print(f'video_name: {video_name}')

    # video_name_dlc_id_labeled = input_video_path_dlc_id_labeled.split('\\')[-1].split('.')[0]
    # print(f'video_name_dlc_id_labeled: {video_name}')

    # output_directory = r'X:\Social-Interaction\Tracking\test_with_hand_transponder_and_piCam\\'
    # print(f'output_directory: {output_directory}')
    if output_directory is None:
        output_directory = input_files_directory
    print('output_directory: ', output_directory )

    # TODO: use regex!
    # video_start_ts = video_name.replace('recording_RP_', '').replace('@', ' ').replace('_', ':').replace('f', '.')
    # print(f'video_start_ts: {video_start_ts}')
    with open(file_start_ts, 'r') as video_start_ts:
        ts_start = video_start_ts.readline()
    print('ts_start: ' + ts_start)
    # Read the video and get some information about it
    vidcap = cv2.VideoCapture(input_video_path)

    _, frame = vidcap.read()
    height, width, layers = frame.shape
    size = (width, height)

    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count/fps
    minutes = int(duration/60)
    seconds = duration%60

    print(
        'fps = ' + str(fps),
        '\nnumber of frames = ' + str(frame_count),
        '\nduration (s) = ' + str(duration),
        '\nduration (m:s) = ' + str(minutes) + ':' + str(seconds),
    )

    vidcap.release()

    return video_name, output_directory, ts_start, frame, width, height, fps, frame_count, duration, minutes, seconds


# match ID
def check_overlap(RFID_df_coords, DLC_coords, RFID_coords):
    '''
    Check if there is an overlap between two coords; meaning if they are in the same area.
    @param: DLC_coords a tuple contains x and y coords.
    @param: RFID_coords a tuple contains x and y coords.
    @return 1 if datapoints overlaps, otherwise 0.
    # example check_overlap((10, 500), (300, 40))
    '''

    # print(DLC_coords, RFID_coords)
    for i in range(len(RFID_df_coords)):
        # RFID_df_coords[RFID_df_coords['area_coords'] == area_coords, 'RFID_reader']
        top_left = RFID_df_coords.area_coords.iloc[i][0]
        bottom_right = RFID_df_coords.area_coords.iloc[i][1]

        # check if both DLC and RFID coords overlap
        if (all([top_left < DLC_coords < bottom_right for top_left, DLC_coords, bottom_right in zip(top_left, DLC_coords, bottom_right)]) and
            all([top_left < RFID_coords < bottom_right for top_left, RFID_coords, bottom_right in zip(top_left, RFID_coords, bottom_right)])):
            return 1
    return 0

def find_all_overlaps(RFID_df_coords, RFID_df_mean, DLC_hdf_centroid, TIME_WINDOW_LENGTH, fps):
    print("Processing RFID-DLC ID matching..")
    DLC_mice_id = DLC_hdf_centroid.columns.levels[0]
    RFID_mice_id = RFID_df_mean['Mouse_ID'].unique()
    frames = len(DLC_hdf_centroid)
    
    mice_product = list(itertools.product(RFID_mice_id, DLC_mice_id))
    DLC_RFID_overlap_dict = dict.fromkeys(mice_product, 0)

    pbar = tqdm.tqdm(total=frames, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
    for frame in range(1, frames):
        for RFID_mouse in RFID_mice_id:    
            # Get RFID mean coords
            x_RFID, y_RFID, _ = fill_mean_RFID_df(RFID_df_mean, RFID_mouse, frame, TIME_WINDOW_LENGTH, fps)
            
            if math.isnan(x_RFID) or math.isnan(y_RFID):
                continue
           
            else:
                for DLC_mouse in DLC_mice_id:
                    # Get DLC coords.
                    # Note that we start at index f_count = 1. The first 0 index is not counted here because the 0 frame is written to the video before the while loop 
                    # and the RFID_df starts at the index f_count = 1 as well
                    # DLC_x_coord = dlc_hdf['DLC_dlcrnetms5_DLC_SI_PiCamDec21shuffle1_102500', DLC_mouse, KEYPOINT_WITH_RFID_TAG, 'x'].iloc[[f_count]].values[0]
                    x_DLC = DLC_hdf_centroid[DLC_mouse, 'x'].iloc[frame] # starts at idx 1
                    y_DLC = DLC_hdf_centroid[DLC_mouse, 'y'].iloc[frame] # starts at idx 1
                
                    # coords are the x and y coords of the RFID reader for `mouse` and f_count.

                    overlap = check_overlap(RFID_df_coords, (x_DLC, y_DLC), (x_RFID.item(), y_RFID.item()))
                    
                    # print(overlap)
                    
                    DLC_RFID_overlap_dict[(RFID_mouse, DLC_mouse)] += overlap

        pbar.update(1)

    pbar.close()

    return DLC_RFID_overlap_dict

def find_id_match(RFID_mice_id, DLC_mice_id, DLC_RFID_overlap_dict):
    matched_IDs = []
    for RFID_id in RFID_mice_id:
        max = 0
        matched_DLC_id = ''
        for DLC_id in DLC_mice_id:
            overlaps = DLC_RFID_overlap_dict.get((RFID_id, DLC_id))
            if overlaps > max:
                max = overlaps
                matched_DLC_id = DLC_id
        matched_IDs.append((RFID_id, matched_DLC_id))
    return np.array(matched_IDs)

def assign_RFID_id_to_DLC(DLC_hdf, DLC_hdf_centroid, matching_reference):
    '''
    Rename the DLC mice name to their corresonding RFID name depending on a reference index, which is calculated by area intersection algorithm. 
    '''
    # Each RFID mouse has a unique DLC mouse
    if  len(matching_reference[:,1]) == len(set(matching_reference[:,1])):
        for mouse in matching_reference:
            DLC_hdf = DLC_hdf.rename(columns={mouse[1]: mouse[0]})
            DLC_hdf_centroid = DLC_hdf_centroid.rename(columns={mouse[1]: mouse[0]})
        return DLC_hdf, DLC_hdf_centroid
    else:
        raise ValueError('Cannot assign a unique ID to the mice. Please try with another longer vidoe.')


# modified version for RFID_df_mean
def find_corresponding_overlap_modified(RFID_df_coords, dlc_hdf_info, frame, DLC_hdf, dlc_id, dlc_coords, RFID_df, RFID_mice_id, TIME_WINDOW_LENGTH, fps):
    '''
    Find the corresponding rfid tag name for a mouse in a specific frame of a given dlc coord in the same frame number.
    The algorithm can be improved by using IOU algorithm (intersection over union). Or also we can use the length of the sceletion instaead of defining bounding boxes.
    
    exampl: 
    # coords = dlc_hdf_copy[scorer, '041917C16C', 'spine3'].iloc[650]
    # find_corresponding_overlap_modified(650, dlc_hdf_copy, '041917C16C', coords, RFID_df_mean[RFID_df_mean.Frame==650])

    '''
    scorer = dlc_hdf_info['scorer'][0]
    DLC_mice_id = DLC_hdf.columns.levels[1]
    bodyparts = dlc_hdf_info['bodyparts']
    corr_rfid_id = []

    # for id_with_coords in rfid_list:
    for id in RFID_df['Mouse_ID'].unique():
        x, y, _ = fill_mean_RFID_df(RFID_df, id, frame, TIME_WINDOW_LENGTH, fps)

        # x = RFID_df_frame.loc[RFID_df_frame['Mouse_ID'] == id, 'x'].values[0]
        # y = RFID_df_frame.loc[RFID_df_frame['Mouse_ID'] == id, 'y'].values[0]
        
        if math.isnan(x) or math.isnan(y):
            continue

        # rfid_pos = list(id_with_coords.values())[0]
        # check if there is an overlap between a specific bodypart and an rfid reader
        if check_overlap(RFID_df_coords, (dlc_coords[0], dlc_coords[1]), (x.item(), y.item())) == 1:
            # corr_rfid_id.append(list(id_with_coords.keys())[0])
            corr_rfid_id.append(id)


    if len(corr_rfid_id) == 0:
        # print('No overlap is found.')
        return 0

    elif len(corr_rfid_id) == 1:
        # print('RFID overlap is found.')

        # check if there are other mice in the same rfid range
        for another_mouse in RFID_mice_id:
            if another_mouse != dlc_id:
                # DLC_hdf = DLC_hdf.sort_index(level=DLC_hdf.index.names)

                for bp in bodyparts:
                    another_mouse_coords =  DLC_hdf[scorer, another_mouse, bp].iloc[frame]  
                    # Do not continue calculating if there is more thatn one dlc mouse in the same rfid range
                    if check_overlap(RFID_df_coords, (dlc_coords[0], dlc_coords[1]), (another_mouse_coords.x, another_mouse_coords.y)) == 1:
                        # print((dlc_coords.x, dlc_coords.y, dlc_id, bp), (another_mouse_coords.x, another_mouse_coords.y, another_mouse, bp))
                        # print('But there are other mice in the same RFID range --> No swapping yet..')
                        return -2
        
        return corr_rfid_id[0]

    # Ensure that we do  not have two rfid reads in the same rfid range.
    else :
        # print('Multiple overlaps are found. Cannot assign dlc to rfid..')
        return -1

def reassign_id(original_df, updated_df, frame, current_id, new_id, updated_mice, bodyparts, scorer):
    """
    assign the coords to the coorect id by overriding the the coords in old id with the new one
    """
    for bp in bodyparts:
        # assign coords from old id to the new id.
        updated_df.loc[frame, (scorer, new_id, bp, 'x')] = original_df.loc[frame, (scorer, current_id, bp, 'x')]
        updated_df.loc[frame, (scorer, new_id, bp, 'y')] = original_df.loc[frame, (scorer, current_id, bp, 'y')]

        if current_id not in updated_mice:
            # erase all coords in all bp in current_id (there is a copy od them in the dict tmp_coords)
            updated_df.loc[frame, (scorer, current_id, bp, 'x')] = math.nan
            updated_df.loc[frame, (scorer, current_id, bp, 'y')] = math.nan
            updated_df.loc[frame, (scorer, current_id, bp, 'likelihood')] = math.nan
    
    return updated_df

def fix_indetity_switching(correction_method, RFID_df_coords, RFID_df, DLC_hdf, dlc_hdf_info, TIME_WINDOW_LENGTH, fps, output_directory, DLC_hdf_centroid, minDistDiff_threshold = None):
    
    if correction_method == 'bp_perFrame':
        DLC_hdf, nr_total_corrections = fix_identity_switching_perFrame("bp", RFID_df_coords, RFID_df, DLC_hdf, dlc_hdf_info, TIME_WINDOW_LENGTH, fps, output_directory)

    elif correction_method == 'centroid_perFrame':
        DLC_hdf, nr_total_corrections = fix_identity_switching_perFrame("centroid", RFID_df_coords, RFID_df, DLC_hdf, dlc_hdf_info, TIME_WINDOW_LENGTH, fps, output_directory, DLC_hdf_centroid)

    elif correction_method == 'bp_frameDistDiff':
        DLC_hdf, nr_total_corrections = fix_identity_switching_frameDistDiff('bp', RFID_df_coords, RFID_df, DLC_hdf, dlc_hdf_info, TIME_WINDOW_LENGTH, fps, minDistDiff_threshold, output_directory, DLC_hdf_centroid=None)
        
    elif correction_method == 'centroid_frameDistDiff':
        DLC_hdf, nr_total_corrections = fix_identity_switching_frameDistDiff('centroid', RFID_df_coords, RFID_df, DLC_hdf, dlc_hdf_info, TIME_WINDOW_LENGTH, fps, minDistDiff_threshold, output_directory, DLC_hdf_centroid)
 
        return DLC_hdf, nr_total_corrections

    elif correction_method == 'all':
        DLC_hdf1, nr_total_corrections1 = fix_identity_switching_perFrame("bp", RFID_df_coords, RFID_df, DLC_hdf, dlc_hdf_info, TIME_WINDOW_LENGTH, fps, output_directory)
        DLC_hdf2, nr_total_corrections2 = fix_identity_switching_perFrame("centroid", RFID_df_coords, RFID_df, DLC_hdf, dlc_hdf_info, TIME_WINDOW_LENGTH, fps, output_directory, DLC_hdf_centroid)
        DLC_hdf3, nr_total_corrections3 = fix_identity_switching_frameDistDiff('bp', RFID_df_coords, RFID_df, DLC_hdf, dlc_hdf_info, TIME_WINDOW_LENGTH, fps, minDistDiff_threshold, output_directory, DLC_hdf_centroid=None)
        DLC_hdf4, nr_total_corrections4 = fix_identity_switching_frameDistDiff('centroid', RFID_df_coords, RFID_df, DLC_hdf, dlc_hdf_info, TIME_WINDOW_LENGTH, fps, minDistDiff_threshold, output_directory, DLC_hdf_centroid)
        
        DLC_hdf = [DLC_hdf1, DLC_hdf2, DLC_hdf3, DLC_hdf4]
        nr_total_corrections = [nr_total_corrections1, nr_total_corrections2, nr_total_corrections3, nr_total_corrections4]
    
    return DLC_hdf, nr_total_corrections

def fix_identity_switching_perFrame(method, RFID_df_coords, RFID_df, DLC_hdf, dlc_hdf_info, TIME_WINDOW_LENGTH, fps, output_directory, DLC_hdf_centroid = None):
        # correct identity switching
    
    # minDistDiff_threshold = 50
    nr_total_corrections = 0
    
    scorer = dlc_hdf_info['scorer'][0]
    DLC_mice_id = DLC_hdf.columns.levels[1]
    bodyparts = dlc_hdf_info['bodyparts']
    RFID_mice_id = RFID_df['Mouse_ID'].unique()

    
    DLC_hdf_updated = DLC_hdf.copy()
    frames = len(DLC_hdf)

    print("Fixing identity switching with method " + method + "_perFrame ...")
    pbar = tqdm.tqdm(total = frames, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
    
    if method == "bp":
        crucial_bp = ['shoulder', 'spine1', 'spine2', 'spine3', 'spine4']
        
        file = open(os.path.join(output_directory, "log_ID-reassignemnt_bp_perFrame.txt"), "w+")

        for f in range(frames):
            
            updated_mice = []
            file.writelines(str(f) + '\n')
            
            for current_id in RFID_mice_id:
                # DLC_hdf = DLC_hdf.sort_index(level=DLC_hdf.index.names)
                for bp in crucial_bp:
                    # dlc_coords = DLC_hdf[f, (scorer, current_id, bp)].iloc[f]#fix warning here!!!!!!!!!!!!
                    dlc_coords_x = DLC_hdf[scorer, current_id, bp, "x"].iloc[f]
                    dlc_coords_y = DLC_hdf[scorer, current_id, bp, "y"].iloc[f]
                    
                    if not (math.isnan(dlc_coords_x) or math.isnan(dlc_coords_y)):
                        break

                # if no coords are found
                if math.isnan(dlc_coords_x) or math.isnan(dlc_coords_y):
                    continue

                # Calculate the binary overlap and find a match.
                new_id = find_corresponding_overlap_modified(RFID_df_coords, dlc_hdf_info, f, DLC_hdf, current_id, (dlc_coords_x, dlc_coords_y), RFID_df, DLC_mice_id, TIME_WINDOW_LENGTH, fps)
                
                if type(new_id) is str:
                    # Correct and swap the mouse id if the already assigned rfid does not match with the new one.
                    if new_id != current_id:      
                        
                        updated_mice.append(new_id)
                        reassign_id(DLC_hdf, DLC_hdf_updated, f, current_id, new_id, updated_mice, bodyparts, scorer)
                        
                        output = f"======== reassign coords from {current_id} to {new_id} at frame {f} ========'"                   
                        file.writelines(output+'\n')
                        # print('======== reassign_id', current_id, 'to', new_id, 'at frame:', f, '========')
                        
                        nr_total_corrections += 1
            pbar.update(1)

    elif method == "centroid":
        
        file = open(os.path.join(output_directory, "log_ID-reassignemnt_centroid_perFrame.txt"), "w+")

        for f in range(frames):
            
            updated_mice = []
            file.writelines(str(f) + '\n')
            
            for current_id in RFID_mice_id:

                dlc_coords_x = DLC_hdf_centroid[current_id, 'x'].iloc[f] # starts at idx 1
                dlc_coords_y = DLC_hdf_centroid[current_id, 'y'].iloc[f] # starts at idx 1

                # if no coords are found
                if math.isnan(dlc_coords_x) or math.isnan(dlc_coords_y):
                    continue

                # Calculate the binary overlap and find a match.
                new_id = find_corresponding_overlap_modified(RFID_df_coords, dlc_hdf_info, f, DLC_hdf, current_id, (dlc_coords_x, dlc_coords_y), RFID_df, DLC_mice_id, TIME_WINDOW_LENGTH, fps)
                
                if type(new_id) is str:
                    # Correct and swap the mouse id if the already assigned rfid does not match with the new one.
                    if new_id != current_id:      
                        
                        updated_mice.append(new_id)
                        reassign_id(DLC_hdf, DLC_hdf_updated, f, current_id, new_id, updated_mice, bodyparts, scorer)
                        
                        output = f"======== reassign coords from {current_id} to {new_id} at frame {f} ========'"                   
                        file.writelines(output+'\n')
                        # print('======== reassign_id', current_id, 'to', new_id, 'at frame:', f, '========')
                        
                        nr_total_corrections += 1
            pbar.update(1)

    file.writelines('nr_total_corrections: ' + str(nr_total_corrections) + '\n')

    file.close()
    pbar.close()


    return DLC_hdf_updated, nr_total_corrections

def fix_identity_switching_frameDistDiff(method, RFID_df_coords, RFID_df, DLC_hdf, dlc_hdf_info, TIME_WINDOW_LENGTH, fps, minDistDiff_threshold, output_directory, DLC_hdf_centroid=None):
    
    DLC_hdf_updated = DLC_hdf.copy()
    frames = len(DLC_hdf)

    print("Fixing identity switching with method " + method + "_frameDistDiff ...")
    pbar = tqdm.tqdm(total = frames, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
    
    # minDistDiff_threshold = 50
    nr_total_corrections = 0
    
    scorer = dlc_hdf_info['scorer'][0]
    DLC_mice_id = DLC_hdf.columns.levels[1]
    bodyparts = dlc_hdf_info['bodyparts']

    RFID_mice_id = RFID_df['Mouse_ID'].unique()
    
    if method == "bp":
    
        crucial_bp = ['shoulder', 'spine1', 'spine2', 'spine3', 'spine4']

        file = open(os.path.join(output_directory, "log_ID-reassignemnt_bp_DistDiff.txt"), "w+")


        for f in range(frames):    
            file.writelines(str(f) + '\n')
            updated_mice = []

            for current_id in RFID_mice_id:
                
                for bp in crucial_bp:
                    x_f = DLC_hdf[scorer, current_id, bp, 'x'].iloc[f]
                    y_f = DLC_hdf[scorer, current_id, bp, 'y'].iloc[f]
        
                    if not (math.isnan(x_f) or math.isnan(y_f)):
                        break

                if math.isnan(x_f) or math.isnan(y_f):
                    continue

                for next_f in range(f+1, frames-1):
                    x_f_next = DLC_hdf[scorer, current_id, bp, 'x'].iloc[next_f]
                    y_f_next = DLC_hdf[scorer, current_id, bp, 'y'].iloc[next_f]

                    # if not pd.isna(DLC_hdf[scorer, current_id, bp, 'x'].iloc[next_f]):
                    if math.isnan(x_f_next) or math.isnan(y_f_next):
                        continue
                
                    dist = math.sqrt((x_f - x_f_next)**2 + (y_f - y_f_next)**2) 

                    if dist > minDistDiff_threshold:
                        # Calculate the binary overlap and find a match.
                        new_id = find_corresponding_overlap_modified(RFID_df_coords, dlc_hdf_info, next_f, DLC_hdf, current_id, (x_f_next, y_f_next), RFID_df, DLC_mice_id, TIME_WINDOW_LENGTH, fps)
                        
                        if type(new_id) is str:
                            # Correct and swap the mouse id if the already assigned rfid does not match with the new one.
                            if new_id != current_id:      
                                
                                updated_mice.append(new_id)
                                reassign_id(DLC_hdf, DLC_hdf_updated, next_f, current_id, new_id, updated_mice, bodyparts, scorer)
                                
                                output = f"======== reassign coords from {current_id} to {new_id} at frame {next_f} ========'"                   
                                file.writelines(output+'\n')
                                # print('======== reassign_id', current_id, 'to', new_id, 'at frame:', f, '========')
                                
                                nr_total_corrections += 1
                                continue # keep working with all next frames if the threshold is fired
                        # break # one bp is enough                    
                    break # if next_f is not nan. We want only the first next_f found
            pbar.update(1)
    

    elif method == "centroid":        

        file = open(os.path.join(output_directory, "log_ID-reassignemnt_centroid_DistDiff.txt"), "w+")

        for f in range(frames):    
            file.writelines(str(f) + '\n')
            updated_mice = []

            for current_id in RFID_mice_id:
                if not pd.isna(DLC_hdf_centroid[current_id, 'x'].iloc[f]):
                    
                    for next_f in range(f+1, frames-1):
                        if not pd.isna(DLC_hdf_centroid[current_id, 'x'].iloc[next_f]):
        
                            x_f = DLC_hdf_centroid[current_id, 'x'].iloc[f]
                            y_f = DLC_hdf_centroid[current_id, 'y'].iloc[f]
                
                            x_f_next = DLC_hdf_centroid[current_id, 'x'].iloc[next_f]
                            y_f_next = DLC_hdf_centroid[current_id, 'y'].iloc[next_f]
                        
                            dist = math.sqrt((x_f - x_f_next)**2 + (y_f - y_f_next)**2) 

                            if dist > minDistDiff_threshold:
                                # Calculate the binary overlap and find a match.
                                new_id = find_corresponding_overlap_modified(RFID_df_coords, dlc_hdf_info, next_f, DLC_hdf, current_id, (x_f_next, y_f_next), RFID_df, DLC_mice_id, TIME_WINDOW_LENGTH, fps)
                                
                                if type(new_id) is str:
                                    # Correct and swap the mouse id if the already assigned rfid does not match with the new one.
                                    if new_id != current_id:      
                                        
                                        updated_mice.append(new_id)
                                        reassign_id(DLC_hdf, DLC_hdf_updated, next_f, current_id, new_id, updated_mice, bodyparts, scorer)
                                        
                                        output = f"======== reassign coords from {current_id} to {new_id} at frame {next_f} ========'"                   
                                        file.writelines(output+'\n')
                                        # print('======== reassign_id', current_id, 'to', new_id, 'at frame:', f, '========')
                                        
                                        nr_total_corrections += 1
                                        continue # keep working with all next frames if the threshold is fired
                    
                            break # if next_f is not nan. We want only the first next_f found
            pbar.update(1)
    
    file.writelines('nr_total_corrections: ' + str(nr_total_corrections) + '\n')

    file.close()
    pbar.close()

    return DLC_hdf_updated, nr_total_corrections


# =====================================================================================================
# =====================================================================================================
# =====================================================================================================


def plot_annotatins_on_video(plot_type,
                            input_video_path, 
                            output_directory,
                            video_name,
                            TIME_WINDOW_LENGTH,
                            RFID_df_coords,
                            RFID_df,
                            DLC_hdf,
                            DLC_hdf_centroid,
                            dlc_hdf_info):
    """
    Cannot plot DLC annotations before ID matching with RFID!
    So before calling with plot_type = DLC, make sure to call `assign_RFID_id_to_DLC`.
    This is important because we want to have both RFID and DLC with the same color.
    """
    scorer = dlc_hdf_info['scorer'][0]
    DLC_mice_id = DLC_hdf.columns.levels[1]
    bodyparts = dlc_hdf_info['bodyparts']
    print(DLC_mice_id)
    RFID_mice_id = RFID_df['Mouse_ID'].unique()

    RFID_id_assigned_to_DLC = DLC_hdf.columns.levels[1][0] in (RFID_mice_id)

    random.seed(9) # to get always the same random colors for each mouse
    font = cv2.FONT_HERSHEY_SIMPLEX
    # RFID_mice_id = RFID_df['Mouse_ID'].unique()

    vidcap = cv2.VideoCapture(input_video_path)
    _, frame = vidcap.read()
    height, width, layers = frame.shape
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    output_video_path = os.path.join(output_directory, video_name + '_dlc_meanRFID-annotation_' + str(TIME_WINDOW_LENGTH) +'sec-Interval.mp4')
    print('output video path name: ' + output_video_path)
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, (width, height))


    # assign a unique color for each mouse and shift its annotation text so that they don't overlap
    id_color_dict = {} # contains mouse id as a key and the values are a unique color for each mouse
    for count, id in enumerate(RFID_df.Mouse_ID.unique()):
        color = ('#%06X' % random.randint(0, 0xFFFFFF)) # generate unique colors for each mouse
        color = ImageColor.getcolor(color, "RGB") # convert colors name to three channels color
        id_color_dict[id] = color # map color to mouse id

    # Draw 3 vertical blue lines with thickness of 2 px
    # xgridlines = (sorted(RFID_df_coords.x.unique()[:3]) + np.diff((sorted(RFID_df_coords.x.unique())))/2).astype(int)
    x_values_topRow = RFID_df_coords.loc[RFID_df_coords['RFID_reader'].str.contains('R2'), 'x']
    xgridlines = sorted(x_values_topRow)[:len(x_values_topRow)-1] + (np.diff(sorted(x_values_topRow))/2).astype(int)


    # append two vertical lines; at beginning and at the end
    xgridlines = sorted(np.append(xgridlines, [0, width]))

    ygridline = int(height/2)

    # draw rectangles: top-left corner and bottom-right corner of rectangle.
    rec_x_tp_left = RFID_df_coords.x - 50
    rec_yp_left = RFID_df_coords.y + 75
    rec_x_bottom_right = RFID_df_coords.x + 50
    rec_y_bottom_right = RFID_df_coords.y - 75

    # txt = RFID_df_coords_scaled_axis.RFID_reader
    txt = RFID_df_coords.RFID_reader

    print('Creating video with annotations..')
    pbar = tqdm.tqdm(total=frame_count, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')

    f_count = 1
    while(vidcap.isOpened):
        pbar.update(1)
        _, frame = vidcap.read()

        # Draw areas. Kepp it uncommentet for now.
        # RFID_df_coords.apply(lambda x: plot_RFID_area(x), axis=1)

        # draw ticks every 10 pixel on the right side
        for tick10 in range(0, height, 10): 
            cv2.line(frame,(width, tick10),(width-20, tick10),(255,255,0),1)

        # draw ticks every 100 pixel on the right side
        for tick100 in range(0, height, 100):        
            cv2.line(frame,(width, tick100),(width-40, tick100),(255,255,0),1)

        # draw ticks every 10 pixel on the bottom side
        for tick10 in range(0, width, 10):
            cv2.line(frame,(tick10, height),(tick10, height-20),(255,255,0),1)

        # draw ticks every 100 pixel on the bottom side
        for tick100 in range(0, width, 100):
            cv2.line(frame,(tick100, height),(tick100, height-40),(255,255,0),1)
        

        # Draw a horizontal blue line with thickness of 2 px
        cv2.line(frame,(0,ygridline),(width, ygridline),(255,0,0),2)

        # Draw 3 vertical blue lines with thickness of 2 px
        for xline in xgridlines:
            cv2.line(frame,(xline, 0),(xline, height),(255,0,0),2)

        # # draw rectangles:top-left corner and bottom-right corner of rectangle.
        # for x1, y1, x2, y2 in zip(rec_x_tp_left, rec_yp_left, rec_x_bottom_right, rec_y_bottom_right):
        #     # filled rectangle
        #     cv2.rectangle(frame,(x1,y2), (x2,y2+30), (0,0,255), -2)
        #     # empty rectangle
        #     cv2.rectangle(frame,(x1,y1), (x2,y2), (0,0,255), 2)

        # draw RFID reader names as text
        for t, x, y in zip(txt, rec_x_tp_left+25, rec_y_bottom_right+20):
            cv2.putText(frame,t,(x,y), font, 0.7,(255,255,255),2,cv2.LINE_AA)

        # draw mice id on the left side
        for count, (id, color) in enumerate(id_color_dict.items()):
            x = 15
            y = 100
            (w, h), _ = cv2.getTextSize(str(id), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame,(0,y-h+count*50), (x+w, y+count*50), (255,255,255), -1)
            cv2.putText(frame,id,(x,y+count*50), font, 0.7,color,2,cv2.LINE_AA)

        # add framenr to the video.
        # for the text background.
        # finds space required by the text so that we can put a background with that amount of width.
        (w, h), _ = cv2.getTextSize(str(f_count), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(frame,(0,0), (w+40, h+30), (255,255,255), -1)
        cv2.putText(frame, str(f_count),(15,30), font, 1,(0,0,255, 0.5),3,cv2.LINE_AA)


        if plot_type == 'all' or plot_type == 'RFID':    
            for m in RFID_mice_id:
                # draw circle for each mouse
                x, y, _ = fill_mean_RFID_df(RFID_df, m, f_count, TIME_WINDOW_LENGTH, fps)
                # if not (x.empty or y.empty or math.isnan(x.values[0]) or math.isnan(y.values[0])):
                if not (math.isnan(x) or math.isnan(y)):
                    cv2.circle(
                        img=frame,
                        center=(int(x.values[0]), int(y.values[0])),
                        radius=10,
                        color=id_color_dict[m], 
                        thickness =-1
                    )


        if plot_type == 'all' or plot_type == 'DLC_bp':
            # draw dlc annotations
            for mouse in DLC_mice_id:
                for bodypart in bodyparts:
                    x = DLC_hdf[scorer, mouse, bodypart, 'x'].iloc[f_count]
                    y = DLC_hdf[scorer, mouse, bodypart, 'y'].iloc[f_count]
                    # print(x.astype(int),y.astype(int))
                    
                    # if the RFID IDs are already assigned to DLC --> print DLC annotations with same RFID color.
                    if RFID_id_assigned_to_DLC:
                        cv2.circle(
                            img=frame,
                            center=(x.astype(int),y.astype(int)),
                            radius=3,
                            # color=id_color_dict[mice_id_swap(mouse)], 
                            color=id_color_dict[mouse], 
                            thickness = -1
                        )
                    
                    # RFID is not assigned to DLC --> plot DLC annotations with random colors 
                    else:
                        cv2.circle(
                            img=frame,
                            center=(x.astype(int),y.astype(int)),
                            radius=3,
                            color=ImageColor.getcolor(('#%06X' % random.randint(0, 0xFFFFFF)), "RGB"),
                            thickness = -1
                        )

        if plot_type == 'all' or plot_type == 'DLC_centroid':

            for DLC_mouse in DLC_mice_id:
                # draw circle for each mouse
                x = DLC_hdf_centroid[DLC_mouse, 'x'].iloc[f_count]
                y = DLC_hdf_centroid[DLC_mouse, 'y'].iloc[f_count]
                # if not (x.empty or y.empty or math.isnan(x.values[0]) or math.isnan(y.values[0])):
                if not (math.isnan(x) or math.isnan(y)):
                    if RFID_id_assigned_to_DLC:
                        cv2.circle(
                            img=frame,
                            center=(x.astype(int),y.astype(int)),
                            radius=7,
                            # color=id_color_dict[mice_id_swap(mouse)], 
                            color=id_color_dict[DLC_mouse], 
                            thickness = 3
                        )
                    
                    # RFID is not assigned to DLC --> plot DLC annotations with random colors 
                    else:
                        cv2.circle(
                            img=frame,
                            center=(x.astype(int),y.astype(int)),
                            radius=3,
                            color=ImageColor.getcolor(('#%06X' % random.randint(0, 0xFFFFFF)), "RGB"),
                            thickness = -1
                        )



        out.write(frame)
        # print(f'frame count: {f_count}')

        # we do not take the last frame in RFID data because westarted at index 1 and this will cause a problem wehn reading DLC data.
        # So we stopp the loop before reaching the maximum video framenumer
        if f_count == frame_count-1:
            break
        
        f_count += 1
        
    vidcap.release()
    out.release()
    pbar.close()
