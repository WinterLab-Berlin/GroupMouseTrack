# ffmpeg -framerate 25 -i recording_RP_2022-05-18__20_57_52.309430.h264 -c copy output.mp4

from subprocess import call

FFMPEG_PATH = r'C:\Program Files\ffmpeg-N-104865-g571e8ca2dd-win64-gpl\ffmpeg-N-104865-g571e8ca2dd-win64-gpl\bin\ffmpeg.exe'
OUTPUT_FILE_EXTENSION = 'mp4'
# FRAMERATE = '25'


input_file_path = r"X:\Social-Interaction\Tracking\short_mice_records\3_m\2022-05-25@14_18_55f896646\2022-05-25@14_18_55f896646_RPi_recording.h264"
print(f'Input file path: {input_file_path}')

input_file_name = input_file_path.split('\\')[-1]
input_file_name = input_file_name.split('.h264')[0] 
print(f'Input file name: {input_file_name}')

output_directory = '\\'.join(input_file_path.split('\\')[:-1]) 
print(f'Output directory: {output_directory}')

output_file_path = output_directory + '\\' + input_file_name + '.' + OUTPUT_FILE_EXTENSION
print(f'Output file path name: {output_file_path}')


call([
    FFMPEG_PATH,
    '-i', input_file_path,
    '-vcodec', 'copy',
    '-f', OUTPUT_FILE_EXTENSION,
    output_file_path
])