"""
Guide for encoding video using FFMPEG with libx264e: https://trac.ffmpeg.org/wiki/Encode/H.264
"""
#import ffmpeg
from subprocess import call
import datetime

#start = '00:00:00'
duration = '01:00:00'
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
FFMPEG_PATH = r'C:\Program Files\ffmpeg-N-104865-g571e8ca2dd-win64-gpl\ffmpeg-N-104865-g571e8ca2dd-win64-gpl\bin\ffmpeg.exe'

output_directory = r'X:\Social-Interaction\Recordings\Thermo_cam\Alexej_thermo_cam\20190410_114156_00000103_24h\\'
input_file_path = r'X:\Social-Interaction\Recordings\Thermo_cam\Alexej_thermo_cam\20190410_114156_00000103.avi'
input_file_name = input_file_path.split('\\')[-1]
input_file_name = input_file_name.split('.')[0] + '_cut.' + input_file_name.split('.')[-1]

print(f'Input file name: {input_file_name}')

# length of the video
# ffmpeg -i recording_RP_2021_12_09--12-02-59.h264 -f null -
# video length is in this line in the variable `time`: frame=2074416 fps=2159 q=-0.0 Lsize=N/A time=23:02:56.64 bitrate=N/A speed=86.3x

# ## recording_RP_2021_12_09--12-02-59: time=23:02:56.64
# ## recording_RP_2021_12_15--14-00-27: time=28:48:55.28

# An example to extract the time
# my_string="hello python world , i'm a beginner "
# print my_string.split("world",1)[1] 


for h in range(0, 24):
    #start = f'{datetime.timedelta(hours = h):02d}:00:00' 
    start = str(datetime.timedelta(hours = h))
    #end = str(datetime.timedelta(hours = h + 1)) # we do not need this if we work with `duration` (set `duration` to 01:00:00 and just update `start`)
    
    output_file_path = output_directory + str(h) + '_' + input_file_name

    print(f'Output file path: {output_file_path}')

    call([
        FFMPEG_PATH,
        '-i', input_file_path,
        '-vcodec', 'copy',
        '-ss', start,
        #'-to', end,
        '-t', duration,
        '-f', OUTPUT_FILE_EXTENSION,
        #'-s', DIMENSIONS,
        #'-b:v', BITRATE,
        #'-r', FRAMERATE,
        #'-preset', PRESET,
        '-threads', '0',
        #'-strict', 'experimental',
        output_file_path
    ])
