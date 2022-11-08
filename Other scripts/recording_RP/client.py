import socket
import time
import picamera

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
client_socket = socket.socket()
client_socket.connect(('192.168.10.19', 8000)) #PC
#client_socket.connect(('192.168.10.18', 8000)) #RPi

# Make a file-like object out of the connection
connection = client_socket.makefile('wb')
try:
    camera = picamera.PiCamera()
    camera.resolution = (1280, 720) 
    #camera.resolution = (int(1280/4), int(720/4)) #640
    
    camera.framerate = 25 #30
    # Start a preview and let the camera warm up for 2 seconds
    #camera.start_preview()
    time.sleep(2)
    # Start recording, sending the output to the connection for 60
    # seconds, then stop
    camera.start_recording(connection, format='h264')
    camera.wait_recording(60*60*24) #36000
    camera.stop_recording()
finally:
    connection.close()
    client_socket.close()
