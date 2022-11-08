from cmd import IDENTCHARS
from ID_matching import *
from RFID import *
from DLC import *


    
def main():

    files_directory = r"E:\Tracking\MOTA_01.32.31--01.34.31__2s"
    # output_directory =  os.getcwd()
    output_directory = r"E:\Tracking\MOTA_01.32.31--01.34.31__2s\identification_output"
    TIME_WINDOW_LENGTH = 2.0 # float number only!
    minDistDiff_threshold = 50
    correction_method = "all"
    plot_type = 'all'
    likelihood_threshold = 0.9
    # Name of the RFID readers. Note that the order is very important. In this order the coords position will by annotated using the left mouse click
    RFID_reader_names = ['R1.1', 'R1.2', 'R1.3', 'R1.4', 
                         'R2.1', 'R2.2', 'R2.3', 'R2.4']

    # get some informations about the data
    input_files_directory, input_video_path, file_start_ts, dlc_file_path, dlc_file_name, RFID_file_path = get_files_paths(files_directory)
    video_name, output_directory, ts_start, frame, width, height, fps, frame_count, duration, minutes, seconds = get_video_info(input_video_path, input_files_directory, file_start_ts, output_directory)

    # Process RFID and DLC
    RFID_df_coords, RFID_df_mean = process_RFID(input_video_path, output_directory, video_name, RFID_file_path, ts_start, duration, fps, height, width, TIME_WINDOW_LENGTH, RFID_reader_names, method='first_video_frame')
    DLC_hdf_centroid, DLC_hdf, dlc_hdf_info =  process_DLC(dlc_file_path, likelihood_threshold)


    # match and assign IDs
    DLC_hdf, DLC_hdf_centroid = match_id(RFID_df_coords, RFID_df_mean, dlc_hdf_info, DLC_hdf, DLC_hdf_centroid, TIME_WINDOW_LENGTH, fps, output_directory)
    save_DLC_hdf(DLC_hdf, output_directory, dlc_file_name, 'without_correction')
    plot_annotatins_on_video(plot_type,
                            input_video_path, 
                            output_directory,
                            video_name + "_" + correction_method,
                            TIME_WINDOW_LENGTH,
                            RFID_df_coords,
                            RFID_df_mean,
                            DLC_hdf,
                            DLC_hdf_centroid,
                            dlc_hdf_info)
    
    # Fix identity switching
    DLC_hdf_corrected, nr_total_corrections = fix_indetity_switching(correction_method, RFID_df_coords, RFID_df_mean, DLC_hdf, dlc_hdf_info, TIME_WINDOW_LENGTH, fps, output_directory, DLC_hdf_centroid, minDistDiff_threshold)
    

    # plot and save annotations
    if type(DLC_hdf_corrected) == list:
        for i, method in zip(range(4), ['bp_perFrame', 'centroid_perFrame', 'bp_frameDistDiff', 'centroid_frameDistDiff']):
            
            save_DLC_hdf(DLC_hdf, output_directory, dlc_file_name, 'matched_with_ID_'+ method)
            
            plot_annotatins_on_video(plot_type,
                        input_video_path, 
                        output_directory,
                        video_name + "_" + method,
                        TIME_WINDOW_LENGTH,
                        RFID_df_coords,
                        RFID_df_mean,
                        DLC_hdf_corrected[i],
                        DLC_hdf_centroid,
                        dlc_hdf_info)

            print('Number of total corrections:', nr_total_corrections[i])
    
    else:
        save_DLC_hdf(DLC_hdf, output_directory, dlc_file_name, 'matched_with_ID_' + correction_method)
        
        plot_annotatins_on_video(plot_type,
                                input_video_path, 
                                output_directory,
                                video_name + "_" + correction_method,
                                TIME_WINDOW_LENGTH,
                                RFID_df_coords,
                                RFID_df_mean,
                                DLC_hdf_corrected,
                                DLC_hdf_centroid,
                                dlc_hdf_info)

        print('Number of total corrections:', nr_total_corrections)



if __name__ == "__main__":
    main()