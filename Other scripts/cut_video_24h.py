"""
Guide for encoding video using FFMPEG with libx264e: https://trac.ffmpeg.org/wiki/Encode/H.264
"""
#import ffmpeg
from subprocess import call
import datetime

start = '00:00:00'
duration = '00:00:1'
start_ts = start.replace(':', '-')
# end = '00:01:00'
# output video dimensions
#DIMENSIONS = '1920x1080'
# output video framerate
#FRAMERATE = '30'
# controls the approximate bitrate of the encode
#BITRATE = '6M'
# encoding speed:compression ratio
#PRESET = 'veryslow'
# output file format
OUTPUT_FILE_EXTENSION = 'mp4'
# relative output directory
#RELATIVE_OUTPUT_DIRECTORY = 'encoded'
# ffmpeg path
FFMPEG_PATH = r'C:\Program Files\ffmpeg-N-104865-g571e8ca2dd-win64-gpl\ffmpeg-N-104865-g571e8ca2dd-win64-gpl\bin\ffmpeg.exe'

output_directory = r"E:\BehaviorDEPOT\SA\\"
input_file_path = r"E:\BehaviorDEPOT\SA\Basler_acA2000-165uc__Side Walls, LEDs  bottom + top centered (cut 1m52s, crf 17, 6500 Kelvin, 1024x800@214)DLC_resnet50_sa-Finger-JointsDec31shuffle1_152000_labeled.mp4"

input_file_name = input_file_path.split('\\')[-1]
input_file_name = input_file_name.split('.')[0]  + '_one_min_cut_' + start_ts + '.' + OUTPUT_FILE_EXTENSION #input_file_name.split('.')[-1]

print(f'Input file name: {input_file_name}')

output_file_path = output_directory + input_file_name #+ OUTPUT_FILE_EXTENSION
print(f'Output file name: {output_file_path}')

# length of the video
# ffmpeg -i recording_RP_2021_12_09--12-02-59.h264 -f null -
# video length is in this line in the variable `time`: frame=2074416 fps=2159 q=-0.0 Lsize=N/A time=23:02:56.64 bitrate=N/A speed=86.3x

# ## recording_RP_2021_12_09--12-02-59: time=23:02:56.64
# ## recording_RP_2021_12_15--14-00-27: time=28:48:55.28


call([
    FFMPEG_PATH,
    '-i', input_file_path,
    '-vcodec', 'copy',
    '-ss', start,
    # '-to', end,
    '-t', duration,
    '-f', OUTPUT_FILE_EXTENSION,
    #'-s', DIMENSIONS,
    #'-b:v', BITRATE,
    #'-r', FRAMERATE,
    #'-preset', PRESET,
    '-threads', '0',
    #'-strict', 'experimental',
    output_file_path,
])