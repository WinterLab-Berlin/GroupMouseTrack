"""
Guide for encoding video using FFMPEG with libx264e: https://trac.ffmpeg.org/wiki/Encode/H.264
"""
#import ffmpeg
from subprocess import call
#import datetime


# 1280 / 720 = 1.7
crf = '17' # default = 23
scale = 'scale=512:-1' # fix the first new dimention and compute the left one (288) automaticaly with the same old ration (1:7)
#start = '00:00:00'
#duration = '00:01:00'
#end = '00:00:10'
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
FFMPEG_PATH = r'C:\Program Files\ffmpeg\bin\ffmpeg.exe'

output_directory = r'Y:\Social-Interaction\Recordings\RPi_cam\compressed\\'
input_file_path = r'Y:\Social-Interaction\Recordings\RPi_cam\recording_RP_2021_12_15--14-00-27.h264'
input_file_name = input_file_path.split('\\')[-1]

print(f'Input file name: {input_file_name}')

# length of the video
# ffmpeg -i recording_RP_2021_12_09--12-02-59.h264 -f null -
# video length is in this line in the variable `time`: frame=2074416 fps=2159 q=-0.0 Lsize=N/A time=23:02:56.64 bitrate=N/A speed=86.3x

# ## recording_RP_2021_12_09--12-02-59: time=23:02:56.64
# ## recording_RP_2021_12_15--14-00-27: time=28:48:55.28

# An example to extract the time
# my_string="hello python world , i'm a beginner "
# print my_string.split("world",1)[1] 

# for h in range(0, 24):
#     start = str(datetime.timedelta(hours = h)) 
#     end = str(datetime.timedelta(hours = h + 1)) 

# fname =  + ' [compressed_scaled_crf=17_scale=512x288]'   
output_file_path = output_directory + input_file_name

print(f'Output file path: {output_file_path}')

call([
    FFMPEG_PATH,
    '-i', input_file_path,
    '-crf', crf,
    '-vf', scale,
    #'-vcodec', 'copy',
    #'-ss', start,
    #'-to', end,
    #'-t', duration,
    '-f', OUTPUT_FILE_EXTENSION,
    #'-s', DIMENSIONS,
    #'-b:v', BITRATE,
    #'-r', FRAMERATE,
    #'-preset', PRESET,
    '-threads', '0',
    #'-strict', 'experimental',
    output_file_path
])
