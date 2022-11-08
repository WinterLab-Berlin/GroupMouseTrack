# ffmpeg -i recording_RP_2021_12_15--14-00-27_cut_first_min.h264 -vf "transpose=2, transpose=2" out-transpose180.mp4

from subprocess import call

FFMPEG_PATH = r'C:\Program Files\ffmpeg\bin\ffmpeg.exe'
OUTPUT_FILE_EXTENSION = 'mp4'


output_directory = r"X:\Social-Interaction\Tracking\\"
input_file_path = r"X:\Social-Interaction\Tracking\recording_RP_2022-05-17-14_08_25.681536.h264"
input_file_name = input_file_path.split('\\')[-1]

print(f'Input file name: {input_file_name}')

output_file_path = output_directory + input_file_name + '--transposed-180'

print(f'Output file path: {output_file_path}')

call([
    FFMPEG_PATH,
    '-i', input_file_path,
    '-f', OUTPUT_FILE_EXTENSION,
    '-vf', "transpose=2,transpose=2",
    output_file_path
])