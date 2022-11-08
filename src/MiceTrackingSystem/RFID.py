from csv import reader
from tkinter import Y
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import math
import cv2
import random
from PIL import ImageColor
import os
import tqdm

def read_RFID_data(RFID_file_path):
    # Read RFID data
    # RFID_file_path = r"test_with_hand_transponder_and_piCam/Sample-22.05.18-Thermo.csv"
    RFID_df = pd.read_csv(RFID_file_path, sep=';', encoding='UTF-16LE')
    return RFID_df


def extract_RFID_coords(RFID_df):
    # Extract coords from RFID dataframe
    RFID_df_coords = RFID_df[RFID_df['DateTime'] == '#ID-Device']
    RFID_df_coords = RFID_df_coords[['IdRFID', 'IdLabel', 'unitLabel']]
    RFID_df_coords[['IdLabel', 'unitLabel']] = RFID_df_coords[['IdLabel', 'unitLabel']].astype(int)

    return RFID_df_coords


def convert_DJ_to_unix_timestampe(rfid_ts):
    '''
    function for converting duplin julian time to utc format
    '''
    try:
        rfid_ts = float(rfid_ts.replace(",", "."))
        #return ephem.Date(rfid_ts)
        
        unix_start_ts = dt.datetime(year=1970, month=1, day=1, hour=0)
        dublin_jd_start_ts = dt.datetime(year=1899, month=12, day=31, hour=12)
        unix_dublin_jd_diff = unix_start_ts - dublin_jd_start_ts
        
        rfid_ts_in_sec = rfid_ts * 60 * 60 * 24
    
        rfid_ts_as_unix = rfid_ts_in_sec - unix_dublin_jd_diff.total_seconds()
        rfid_ts = dt.datetime.utcfromtimestamp(rfid_ts_as_unix)
        # rfid_ts = dt.datetime.strftime(rfid_ts, '%Y-%m-%d %H:%M:%S')
        return rfid_ts
        
    except:
        return rfid_ts


def clean_RFID_data(RFID_df, RFID_df_coords):
    # Keep only relevant rows
    RFID_df = RFID_df[RFID_df['DateTime'] != '#ID-Device']

    # Keep only relevant cols
    RFID_df = RFID_df[['DateTime', 'IdRFID', 'unitLabel', 'eventDuration', 'senseRFIDrecords']]

    # convert duplin julian time to utc format
    RFID_df['DateTime'] = RFID_df['DateTime'].apply(convert_DJ_to_unix_timestampe)

    # Rename cols 
    RFID_df_coords.rename(columns = {'IdLabel':'x', 'unitLabel':'y', 'IdRFID':'RFID_reader'}, inplace=True)
    RFID_df.rename(columns = {'DateTime': 'DateTime_start', 'IdRFID':'Mouse_ID', 'unitLabel':'RFID_reader'}, inplace=True)
    
    # sort dataframe by the datetime column
    RFID_df = RFID_df.sort_values(by=['DateTime_start'], ignore_index=True)

    return RFID_df, RFID_df_coords


def shift_RFID_date(RFID_df):
    # shift the timestamps only one time
    # run_once = False

    # Shift the dates in the RFID dataframe backwards  so that they match the timestamp of the video (2 days and 12 hours)
    # if not run_once:
    RFID_df['DateTime_start'] = RFID_df['DateTime_start'].apply(lambda ts: ts - dt.timedelta(days=2))
    RFID_df['DateTime_start'] = RFID_df['DateTime_start'].apply(lambda ts: ts + dt.timedelta(hours=12))
    # RFID_df['DateTime'] = RFID_df['DateTime'].apply(lambda ts: dt.datetime.strftime(ts, '%Y-%m-%d %H:%M:%S'))

    # insert end event time
    RFID_df.insert(2, 'DateTime_end', RFID_df['DateTime_start'] + pd.to_timedelta(RFID_df['eventDuration'], unit="ms"))

    # run_once = True

    return RFID_df


def cut_RFID_data(RFID_df, ts_start, duration):
    # Cut RFID dataframe so that its starting timestampe mathces the video starting time

    # global ts_start

    # Convert video start time from string to date format
    # ts_start = dt.datetime.strptime(video_start_ts, '%Y-%m-%d %H:%M:%S.%f')
    ts_start = dt.datetime.strptime(ts_start, '%Y-%m-%d %H:%M:%S.%f')

    # Add 2 seconds to the video starting time because the RaspPi camera waits 2s before it starts recording
    # ts_start += dt.timedelta(seconds=2) # add tw sec because of the RPiCam waiting before recording
    # print(ts_start)

    ts_end = ts_start + dt.timedelta(seconds=duration)

    # Keep only data which starts after the video start timestamp
    RFID_df = RFID_df[RFID_df['DateTime_start'] >= ts_start]
    RFID_df = RFID_df[RFID_df['DateTime_end'] <= ts_end]

    # sort dataframe by the datetime column
    RFID_df = RFID_df.sort_values(by=['DateTime_start'], ignore_index=True)

    RFID_df.dropna(inplace=True)

    return RFID_df, ts_start


def add_frame_to_RFID(RFID_df, ts_start, fps):
    """
    calculate the corresponding frame number of each detection in the RFID dataframe
    """

    def calc_frame_number(row, ts_start, fps):
        '''
        Add frame nr. column to the RFID df.
        RPi camera video captures fps = 25 .
        1f takes (1/25 = 0.04s) = (0.04*1000 = 40ms)
        '''
        # TODO: do  not hardcode the fps
        # get the timestape of the given row
        ts = row['DateTime_start']
        
        # calcutate the time difference between the video starting time and the time of the given detecetion in the RFID dataframe 
        ts_diff = (ts - ts_start).total_seconds()
        
        # calculate teh corresponding video frame number of the given ts of the detection in the RFID dataframe
        frame = math.floor(ts_diff * fps) #+ 1

        # print(ts_start, ts, ts_diff, frame)

        return frame


    RFID_df['Frame'] = RFID_df.apply(lambda x: calc_frame_number(x, ts_start, fps), axis=1)

    # Reorder columns
    RFID_df = RFID_df.reindex(columns=['Frame', 'DateTime_start', 'DateTime_end','Mouse_ID', 'RFID_reader', 'eventDuration', 'senseRFIDrecords'])

    return RFID_df


# not used for now. Instead use `pick_RFID_reader_pos()`
def scale_RFID_coords_manually(RFID_df_coords):
    # if not run_once:
        # RFID_df_coords_scaled_axis = RFID_df_coords.copy(deep=True)
        # RFID_df_coords_scaled_axis[['x', 'y']] = RFID_df_coords_scaled_axis[['x', 'y']].apply(lambda x: x * 7)
        # RFID_df_coords = RFID_df_coords_scaled_axis

    # RFID_df_coords['x'] = list(map(shift_x_coords, RFID_df_coords['x']))  # shift x coords
    RFID_df_coords[['y']] = RFID_df_coords[['y']].apply(lambda y: y*7 + 10)   # shift y coords

    RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R1.1'), 'x'] = RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R1.1'), 'x'] * 7 + 2
    RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R2.1'), 'x'] = RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R2.1'), 'x'] * 7 + 2

    RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R1.2'), 'x'] = RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R1.2'), 'x'] * 7 + 15
    RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R2.2'), 'x'] = RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R2.2'), 'x'] * 7 + 15

    RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R1.3'), 'x'] = RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R1.3'), 'x'] * 7 + 35
    RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R2.3'), 'x'] = RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R2.3'), 'x'] * 7 + 35
    
    RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R1.4'), 'x'] = RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R1.4'), 'x'] * 7 + 55
    RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R2.4'), 'x'] = RFID_df_coords.loc[(RFID_df_coords['RFID_reader'] == 'R2.4'), 'x'] * 7 + 55

    return RFID_df_coords



# used by `pick_RFID_reader_pos()`
def click_on_image(event, x, y, flags, params):
    '''
    Mouse callback function to check left  click
    Only the first X mouse clicks will be uesed!, where X corresponds to the number of RFID readers  
    '''
    # global coord_x, coord_y # coord_x, coord_y = -1, -1
    
    if event == cv2.EVENT_LBUTTONDOWN:

        try:
            RFID_reader_name = RFID_reader_names_copy.pop(0)    
            RFID_reader_manual_coords.append([x,y])
            # print(f'{RFID_reader_name}: ({x}, {y})')

            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, ' (' + str(x) + ', ' + str(y) + ')', (x-40, y), font, 0.5, (255, 255, 0), 2)
            cv2.putText(img, RFID_reader_name , (x-20, y-20), font, 0.5, (255, 255, 0), 2)
            cv2.circle(img, (x, y+20), 6, (255, 255, 0), -1)

            cv2.imshow('image', img)

        except:
            print("You have reached the maximum number of RFID readers! Please close the window to continue processing.")
    


def pick_RFID_reader_pos(RFID_reader_names, method, RFID_df_coords, input_video_path, img_path=None):
    """
    @param method either `image` or `first_video_frame`
    """
    global RFID_reader_names_copy, RFID_reader_manual_coords
    RFID_reader_names_copy = RFID_reader_names.copy()
    RFID_reader_manual_coords = []

    print("Please left-click with the mouse on the image to select the coordinate of the RFID reader positions. Be aware of the order!")  

    global img
    if method == 'image':
        # select image
        img = cv2.imread(img_path)

    elif method == 'first_video_frame':
        # extract first frame from the video
        vidcap = cv2.VideoCapture(input_video_path)
        _, img = vidcap.read()
        vidcap.release()
    else:
        raise Warning ("Wrong paramater for the method of exctracting an image for determining RFID readers coordination")  


    cv2.imshow('image', img)
    

    cv2.setMouseCallback('image', click_on_image)
    cv2.waitKey(0)
    
    cv2.destroyAllWindows()

    # RFID_dict = dict(zip(RFID_reader_names, RFID_reader_manual_coords))

    for reader_name, coords in zip(RFID_reader_names, RFID_reader_manual_coords):
        RFID_df_coords.loc[RFID_df_coords['RFID_reader'] == reader_name, 'x'] = coords[0]
        RFID_df_coords.loc[RFID_df_coords['RFID_reader'] == reader_name, 'y'] = coords[1]


    return RFID_df_coords



def add_RFID_area(df, height, width):
    
    ORIGIN_POS = 0
    Y_MIDDLE_POS = int(height/2)
    END_POS = width

    # area_width_coords = (sorted(df.x.unique()[:3]) + np.diff((sorted(df.x.unique())))/2).astype(int)
    x_values_topRow = df.loc[df['RFID_reader'].str.contains('R2'), 'x']
    area_width_coords = sorted(x_values_topRow)[:len(x_values_topRow)-1] + (np.diff(sorted(x_values_topRow))/2).astype(int)

    area_width_topRow_coords = sorted(np.append(area_width_coords, ORIGIN_POS))
    area_width_bottomRow_coords = sorted(np.append(area_width_coords, END_POS))

    area_height_topRow_coords = [ORIGIN_POS, Y_MIDDLE_POS]
    area_height_bottomRow_coords = [Y_MIDDLE_POS, END_POS]


    def calc_RFID_area(row):
        """
        calculate the area of each RFID reader and append it to the given dataframe (RFID_df_coords!).
        """
        
        RFID_pos = (row.x, row.y)

        for height_top, height_bottom in zip(area_height_topRow_coords, area_height_bottomRow_coords):
        
            for width_top, width_bottom in zip(area_width_topRow_coords, area_width_bottomRow_coords):

                top_coords = (width_top, height_top)
                bottom_coords = (width_bottom, height_bottom)

                check_area_pos = all(top < RFID_pos < bottom for top, RFID_pos, bottom in zip(top_coords, RFID_pos, bottom_coords))
            
                if check_area_pos:
                    area_coords = ((width_top, height_top), (width_bottom-1, height_bottom-1))  #subtract one pixel from the bottom side to avoid area overlapping      
                    return area_coords
                
    df['area_coords'] = df.apply(lambda x: calc_RFID_area(x), axis=1)


def calc_weight(case_df, duration_in_window):
    duration_in_window = duration_in_window.replace(0.0, 1)
    duration_in_window_percentage = duration_in_window / case_df['eventDuration']
    nr_reads_in_window = duration_in_window_percentage * case_df['senseRFIDrecords']
    weight = duration_in_window * nr_reads_in_window
    return weight


def from_coords_to_reader(RFID_df_coords, x, y):
    for i in range(len(RFID_df_coords)):
        area_coords = RFID_df_coords.area_coords.loc[i]        
        RFID_reader = RFID_df_coords.RFID_reader.loc[i] 
       
        # if math.isnan(x):
        #     return math.nan
        if (x > area_coords[0][0] and
              y > area_coords[0][1] and 
              x < area_coords[1][0] and 
              y < area_coords[1][1]):
            return RFID_reader


def calc_mean_RFID_coords(RFID_df_coords, RFID_df, mouse_ID, start_window, end_window):
    
    # All scenarios of RFID events in one window.
    # (3)      ##|##########|###
    # (6)        |          | #######
    # (5)        |      ####|#####
    # (4)        |   ####   |
    # (2)      ##|######    |
    # (1)    ### |          |          
    #       -------------------------------
    #            |    1s    |    1s    |


    def from_readerName_to_coords(RFID_row):
        '''
        Find coords of a given reader name
        '''
        x = RFID_df_coords.loc[RFID_df_coords.RFID_reader == RFID_row.RFID_reader, 'x']
        y = RFID_df_coords.loc[RFID_df_coords.RFID_reader == RFID_row.RFID_reader, 'y']
        return x.values[0], y.values[0]


    m_RFID_df = RFID_df.loc[RFID_df['Mouse_ID'] == mouse_ID]

    # m_RFID_df.loc[(m_RFID_df['DateTime_start'] < start_window) & (m_RFID_df['DateTime_end'] < start_window)] # 1 --> ignore data
    # m_RFID_df.loc[(m_RFID_df['DateTime_start'] > start_window) & (m_RFID_df['DateTime_start'] >= end_window)] # 6 --> ignore data

    # Find time bins
    case_2 = m_RFID_df.loc[(m_RFID_df['DateTime_start'] < start_window) & (m_RFID_df['DateTime_end'] <= end_window) & (m_RFID_df['DateTime_end'] >= end_window)] # 2
    case_3 = m_RFID_df.loc[(m_RFID_df['DateTime_start'] < start_window) & (m_RFID_df['DateTime_end'] > end_window)] # 3
    case_4 = m_RFID_df.loc[(m_RFID_df['DateTime_start'] > start_window) & (m_RFID_df['DateTime_start'] < end_window) & (m_RFID_df['DateTime_end'] <= end_window)] # 4 --> take all of them
    case_5 = m_RFID_df.loc[(m_RFID_df['DateTime_start'] > start_window) & (m_RFID_df['DateTime_start'] < end_window) & (m_RFID_df['DateTime_end'] > end_window)] # 5

    # Adjust ts and calculate durations to fit the window 
    case_2_duration_in_window = (case_2['DateTime_end'] - start_window).dt.total_seconds() * 1000
    case_3 = case_3.assign(DateTime_start=start_window, DateTime_end=end_window)
    # case_3.loc[case_3['DateTime_start'] != 0, 'DateTime_start'] = start_window
    # case_3.loc[case_3['DateTime_end'] != 0, 'DateTime_end'] = end_window
    case_3_duration_in_window = (case_3['DateTime_end'] - case_3['DateTime_end']).dt.total_seconds() * 1000
    case_4_duration_in_window = (case_4['DateTime_end'] - case_4['DateTime_start']).dt.total_seconds() * 1000
    case_5_duration_in_window = (end_window - case_5['DateTime_start']).dt.total_seconds() * 1000

    # calculate the weight (duration * nr of reads in the time bin)
    case_2_weight = calc_weight(case_2, case_2_duration_in_window)
    case_3_weight = calc_weight(case_3, case_3_duration_in_window)
    case_4_weight = calc_weight(case_4, case_4_duration_in_window)
    case_5_weight = calc_weight(case_5, case_5_duration_in_window)

    # calculate the pwecentage of each weight
    sum_events_weights = case_2_weight.sum() + case_3_weight.sum() + case_4_weight.sum() + case_5_weight.sum()
    case_2_weight /= sum_events_weights
    case_3_weight /= sum_events_weights
    case_4_weight /= sum_events_weights
    case_5_weight /= sum_events_weights

    x_sum = math.nan
    y_sum = math.nan

    for (case, weight) in zip([case_2, case_3, case_4, case_5], [case_2_weight, case_3_weight, case_4_weight, case_5_weight]):
        coords = case.apply(lambda x: from_readerName_to_coords(x), axis=1)
        for w, (x, y) in zip(weight, coords):
            x_sum = np.nansum([x_sum, w * x])
            y_sum = np.nansum([y_sum, w * y])


    if not math.isnan(x_sum):
        x_sum = int(x_sum)

    if not math.isnan(y_sum):
        y_sum = int(y_sum)

    # print(x_sum, y_sum)
    return x_sum, y_sum


def calc_frame_from_ts(ts_start, ts, fps):
    '''
    RPi camera video captures fps = 25 .
    1f takes (1/25 = 0.04s) = (0.04*1000 = 40ms)
    '''
    # get the timestape of the given row
    # ts = row['DateTime']
    
    # calcutate the time difference between the video starting time and the time of the given detecetion in the RFID dataframe 
    ts_diff = (ts - ts_start).total_seconds()
    
    # calculate teh corresponding video frame number of the given ts of the detection in the RFID dataframe
    frame = math.floor(ts_diff * fps) #+ 1

    # print(ts_start, ts, ts_diff, frame)

    return frame


def create_full_mean_df_RFID_in_time_window(RFID_df_coords, RFID_df, ts_start, fps, TIME_WINDOW_LENGTH,):
    print('Processing final RFID dataframe of each mouse...')
    pbar = tqdm.tqdm(total = len(RFID_df['Mouse_ID'].unique()), bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
    # TIME_WINDOW_LENGTH = 1
    RFID_mice_id = RFID_df['Mouse_ID'].unique()

    # replace 0 eventDuration with one sec
    RFID_df['eventDuration'].replace([0.0], 1, inplace=True)

    frame = []
    mouse_id = []
    x = []
    y = []
    reader = []

    for mouse in RFID_mice_id:

        first_detection_ts = min(RFID_df.loc[RFID_df['Mouse_ID'] == mouse, 'DateTime_start'])
        last_detection_ts = max(RFID_df.loc[RFID_df['Mouse_ID'] == mouse, 'DateTime_end'])
        mouse_duration = pd.Timedelta(last_detection_ts - first_detection_ts).seconds

        # for sec in range(TIME_WINDOW_LENGTH, mouse_duration, TIME_WINDOW_LENGTH):
        for sec in np.arange(TIME_WINDOW_LENGTH, mouse_duration, TIME_WINDOW_LENGTH):
            start_window = first_detection_ts + dt.timedelta(seconds = sec-TIME_WINDOW_LENGTH)
            end_window = first_detection_ts + dt.timedelta(seconds = sec)
            coords = calc_mean_RFID_coords(RFID_df_coords, RFID_df, mouse, start_window, end_window)
        
            start_frame = calc_frame_from_ts(ts_start, start_window, fps)
            end_frame = calc_frame_from_ts(ts_start, end_window, fps)
            
            for f in range(start_frame, end_frame):
                frame.append(f)
                mouse_id.append(mouse)
                x.append(coords[0])
                y.append(coords[1])
                reader.append(from_coords_to_reader(RFID_df_coords, coords[0], coords[1]))
        pbar.update(1)
            

    RFID_df = pd.DataFrame(list(zip(frame, mouse_id, x, y, reader)), columns=['Frame', 'Mouse_ID', 'x', 'y', 'Reader'])
    pbar.close()
    return RFID_df


def create_mean_df_RFID_in_time_window(RFID_df_coords, RFID_df, ts_start, fps, TIME_WINDOW_LENGTH,):
    if not isinstance(TIME_WINDOW_LENGTH, float):
        raise Exception("Unauthorized TIME_WINDOW_LENGTH! Numbre must be float and not integer.")
    print('Processing final RFID dataframe of each mouse...')
    pbar = tqdm.tqdm(total = len(RFID_df['Mouse_ID'].unique()),bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')

    RFID_mice_id = RFID_df['Mouse_ID'].unique()

    # replace 0 eventDuration with one sec
    RFID_df['eventDuration'].replace([0.0], 1, inplace=True)

    frame = []
    mouse_id = []
    x = []
    y = []
    reader = []

    for mouse in RFID_mice_id:

        first_detection_ts = min(RFID_df.loc[RFID_df['Mouse_ID'] == mouse, 'DateTime_start'])
        last_detection_ts = max(RFID_df.loc[RFID_df['Mouse_ID'] == mouse, 'DateTime_end'])
        mouse_duration = pd.Timedelta(last_detection_ts - first_detection_ts).seconds

        # for sec in range(TIME_WINDOW_LENGTH, mouse_duration, TIME_WINDOW_LENGTH):
        for sec in np.arange(TIME_WINDOW_LENGTH, mouse_duration, TIME_WINDOW_LENGTH):
            start_window = first_detection_ts + dt.timedelta(seconds = sec-TIME_WINDOW_LENGTH)
            end_window = first_detection_ts + dt.timedelta(seconds = sec)
            coords = calc_mean_RFID_coords(RFID_df_coords, RFID_df, mouse, start_window, end_window)

            if not math.isnan(coords[0]):
                start_frame = calc_frame_from_ts(ts_start, start_window, fps)
                
                frame.append(start_frame)
                mouse_id.append(mouse)
                x.append(coords[0])
                y.append(coords[1])
                reader.append(from_coords_to_reader(RFID_df_coords, coords[0], coords[1]))
        pbar.update(1)
            

    RFID_df = pd.DataFrame(list(zip(frame, mouse_id, x, y, reader)), columns=['Frame', 'Mouse_ID', 'x', 'y', 'Reader'])
    pbar.close()
    return RFID_df


def fill_mean_RFID_df(RFID_df, mouse, frame, TIME_WINDOW_LENGTH, fps):
    frames = list(filter(lambda x: x <= frame, RFID_df.loc[RFID_df['Mouse_ID'] == mouse, 'Frame']))
    if len(frames) > 0:
        first_frame_in_window = max(frames)

        if frame < (first_frame_in_window +  math.floor(TIME_WINDOW_LENGTH * fps)):
            x = RFID_df.loc[((RFID_df['Mouse_ID'] == mouse) & (RFID_df['Frame'] == first_frame_in_window)), 'x'] 
            y = RFID_df.loc[((RFID_df['Mouse_ID'] == mouse) & (RFID_df['Frame'] == first_frame_in_window)), 'y'] 
            reader = RFID_df.loc[((RFID_df['Mouse_ID'] == mouse) & (RFID_df['Frame'] == first_frame_in_window)), 'Reader'] 
            # print(x, y, reader)
            return x, y, reader
        # else:
            # return math.nan, math.nan, math.nan
    # else:
    return math.nan, math.nan, math.nan



# def shift_x_coords(x):
#     # shift the coords only one time
#     # scale coords 
#     # hardcode shifting x coords so that they match corresponding position in the video.
#     # This approach is NOT good enough because of the distortion of the Pi camera.

#     # xleft_coord = 200
#     # x_right_coord = 1180
#     # y_up_coord = 225
#     # y_buttom_coord = 500

#     # x_RFID_coords = [i for j in (range(xleft_coord, x_right_coord, int((x_right_coord - xleft_coord) / 4)), range(xleft_coord, x_right_coord, int((x_right_coord - xleft_coord) / 4))) for i in j]
#     # y_RFID_coords = [y_up_coord] * 4 + [y_buttom_coord] * 4

#     # RFID_df_coords['x'] = x_RFID_coords
#     # RFID_df_coords['y'] = y_RFID_coords


#     # before scaling the coords, coorect the position of the RFID Readers by shifting thier values on the x-axis one pixle to the left, 
#     # Not necessary anymore because of hardcoding the coords.
#     # RFID_df_coords['x'] = RFID_df_coords['x'].apply(lambda x:  x-1 if (x == 99 or x == 124) else x)
#     # RFID_df_coords


#     # check the distances between the readers
#     # print(RFID_df_coords.x.unique()[:3])
#     # print(np.diff((RFID_df_coords.x.unique())))
#     # print(RFID_df_coords.x.unique()[:3] + np.diff((RFID_df_coords.x.unique())))

#     # scale coords 
#     # hardcode shifting x coords so that they match corresponding position in the video.

#     rfid_df = RFID_df_coords[RFID_df_coords.x == x].iloc[0]
#     x *= 7
    
#     if rfid_df['RFID_reader'] == 'R1.1' or rfid_df['RFID_reader']  == 'R2.1':
#         x += 2 
#     elif rfid_df['RFID_reader'] == 'R1.2' or rfid_df['RFID_reader']  == 'R2.2':
#         x += 15
#     elif rfid_df['RFID_reader'] == 'R1.3' or rfid_df['RFID_reader']  == 'R2.3':
#         x += 35
#     elif rfid_df['RFID_reader'] == 'R1.4' or rfid_df['RFID_reader']  == 'R2.4':
#         x += 55
    
#     return x
