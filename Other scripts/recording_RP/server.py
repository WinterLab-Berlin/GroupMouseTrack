from genericpath import exists
from importlib.resources import path
import socket
import subprocess
from datetime import datetime
import os

path_date = datetime.now().strftime("%Y-%m-%d@%H_%M_%Sf%f")


# define the video name as a video creating datetime.
video_name = os.path.join(path_date, path_date + '_RPi_recording.h264')
print(video_name)
# create a text file to save the first timestampe of the video.
file_path_start_ts = os.path.join(path_date, path_date + '_start_ts.txt')

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')

try: 


    while True:
        # Repeatedly read 1k of data from the connection and write it to
        # the media player's stdin
        data = connection.read(1024)

        # check if the folder exist
        if not os.path.exists(path_date):
            try:
                # create a directory to save the video and the ts file inside it, if it does not exist.
                os.makedirs(path_date, exist_ok=True)
                print('New directory is created: ' + path_date)

                # create the video
                binary_data = open(video_name, 'wb')    
                
                # check if the text file with the ts of the video does exist
                if not os.path.exists(file_path_start_ts):

                    # create a text file and save the actual timestampe of the video starting time
                    file_start_ts = open(file_path_start_ts, 'w+')
                    try:
                        # write the timestampe of the first frame inside a file
                        file_start_ts.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
                    except:
                        print(f"Cannot write into file '{file_path_start_ts}'!")
                    finally:
                        file_start_ts.close()

            except:
                print(f"Directory '{path_date}' cannot be created!")

        try:
            binary_data.write(data)    
        except:
            print(f"Cannot write into file '{file_path_start_ts}'!")
  
        if not data:
            break
finally:
    connection.close()
    server_socket.close()
    binary_data.close()
