# Table of Contents
[1. Motivation](#motivation)

[2. Overview](#overview)

[2. Experimental setup](#Experimental-setup)

# Motivation
Locating and tracking moving objects and organisms in spatio-temporal data finds application in a wide variety research. For instance, in the field of neuroscience, social interactions are analyzed to provide insights into healthy and pathological cognitive and emotional processes. To realize the location and tracking aspect of such tasks, there exist a variety of methods which can extract and process the necessary information from video data.
In its simplest form, a human annotator can locate and track points of interest within and across subsequent frames. This task, however, is mundane and time-consuming, quickly leading to fatigue and subsequently errors in annotation. Especially demanding are multi-individual scenarios showing fast movements.
Computer vision provides sophisticated methods to automate parts of this process. These methods traditionally rely on marking several body parts of the animal to accomplish location and tracking. While such a solution can perform highly accurate pose estimation, placing markers on animals to track various body parts can negatively impact an animals natural behavior and possibly alter research results.
Recently, novel deep learning-based methods have simplified these techniques and relieved the need for attaching physical markers to the animals. Deep learning algorithms can learn to predict and track the positions of specific body parts across multiple animals from videos frames without being explicitly instructed. Compared to prior methodologies, this method provides a faster and more accurate automated prediction of animal posture.

The experiment was carried out in the Winter laboratory at Humboldt University.


# Overview
The project applies an end-to-end solution based on Deep Neural Networks (DNN) with the help of DeepLabCut (DLC), a Python framework built on TensorFlow, to investigate its viability in the context of pose estimation and tracking of mice in an experimental setup, which solely rely on raw video data as input.

The experiment uses a single, low-cost camera to record multiple RFID-tagged mice in a cage equipped with RFID sensors. In each recording session, laboratory animals are recorded and tracked for long time scales, allowing for the capture of a diversity of social interactions and building the basis for social behavior studies. Though not required for tracking, the RFID data can be used to detect potential identity swaps made by the trained DNN as well as match the mice’s RFIDs to their location in video. The final model we provide achieved a test error of 4.9 pixels, which is similar to the labelling variability between humans (5.2 pixels).


todo-conclusion: [[We utilized the DeepLabCut toolbox to track and localize several mice keypoints in complex social inter- actions without the need for physical markers.
Besides DeepLabCut, we utilized an RFID (Radio Frequency Identification) system to identify and dif- ferentiate between various mice, that are microchipped with an RFID tag. Furthermore, we used RFID tagging to automate periodic correction of mice identity switches without the need for manual inspec- tion. One limitation of employing RFID system in order to identify multiple mice, is that the RFID tag detections are not precise as the neural network predictions, especially when numerous mice are housed in an 820 𝑐𝑚2 cage. Therefore, utilizing an RFID system to correct identity switches may result in cer- tain identity errors, which occur when a mouse overlaps with a mismatched RFID tag, and FN detections, which can arise when just one of the switched Identities is corrected.

In our experiment, we provide a set of scripts that combines DLC and the RFID system to perform pose estimation, tracking, and identification of a horde of interacting mice in a laboratory home cage. Researchers can use our software to record videos over long times scales and analyze novel videos from comparable experimental settings. We developed our scripts to be scalable, customizable and easy to use. In addition, we designed an automated method allowing the user to dynamically specify the RFID reader positions on the video frame with no prior-configuration. This is beneficial for ensuring consistency when changing the camera position. The RFID system we used consists of eight RFID readers; nevertheless, our scripts are capable to function with any number of RFID readers. Our trained model has been trained on images containing three mice, but this is not a strict upper bound. For inference, users can run the experiment with more or less mice.]]

The objective of this experiment is: 1) tracking and localizing various body parts, 2) identify multiple identical-looking mice across a broad collection of behaviors and 3) correct potential identity switch between the animals. In this experiment, we provide a set of scripts that is implemented in python and completely automated and simple to run, integrating the DeepLabCut toolbox with the RFID technology. This guide will go you through three main stages: 
* **Stage I: Data acquisition:** 
    All necessary steps to record the video data and to gather RFID detections will be explained at this stage

* **Stage II: Pose estimation and multi-animal tracking:**
    Using DLC, the recorded videos will be analyzed and evaluated using our trained model. The final output at this stage will be tracks of postures for each individual as h5/CSV files and labeled videos with dummy identities.

* **Stage III: Animal identification and verification:**
    The RFID detections will be used to replace DLC dummy IDs with their associated RFID tag. Furthermore, we provide other set of scripts for verifying and re-matching the mice ID whenever a potential ID swap made by DLC has been detected.


# Experimental setup

The experiment can be performed in a mouse home-cage that should house the RFID implemented mice. Above the mice’s home-cage, a camera can be placed. We used a small 5 Megapixel Raspberry Pi camera (any compatible camera would work) with two infrared LEDs, that automatically switches between day and night mode automatically. The Pi-Camera is need to be connected to a Raspberry Pi with the Raspbian operating system. The RFID reader device must be suited underneath the customized home-cage and connected to a Windows PC via an Ethernet wire as shown in the following figure:
<figure>
  <img src="real-setup-overview.png" alt="Experimental setup overview" width="400"/>
  <!-- <figcaption>Experimental setup overview.</figcaption> -->
</figure>


# Installation
You can clone the scripts from GitHub by firing up the shell and typing:

```sh
git clone https://github.com/WinterLab-Berlin/GroupMouseTrack.git
```
Alternatively, you can go to the Git repository and download the package manually.

<!-- ![abstract-expermental-protocol](abstract-expermental-protocol.png) -->
<figure>
  <img src="abstract-expermental-protocol.png" alt="my alt text" width="400"/>
  <!-- <figcaption>Experimental setup overview.</figcaption> -->
</figure>

# Stage I: Data Acquisition
## 1. RFID detection
RFID data is acquired on the Windows PC. The RFID data detections provide a series of events in a CSV file that has information about each mouse (its identity) that has been scanned by a reader, as well as its timestamp and location. RFID reads can be rogue and imprecise, in the sense that a tag can be read from multiple readers in a single time segment (i.e. one second), implying that the RFID device estimates the mouse position. The detection is done using the software x-todo. Run the application and start recording. This step can be done either before or after the video recording. However, we recommend starting collecting the RFID data before the video recording session stars.

todo : add a screenshot here of the RFID application.

## 2. Video Recording
We use the communication protocol SSH to enable the communication between the RPi and the Windows PC (also possible via VNC). Image frames are encoded to an H264 video file. Additionally, the timestamp of the first captured frame will be stored in a CSV file. This step will be important later on when we synchronize videos with RFID data to perform the ID matching process. For the video recording, we used a simple network communication protocol for sending a continual stream of video frames. We provide two scripts: a server, that runs on the Windows machine and listens/waits for a connection from the Raspberry Pi, and a client that runs on the RPi and sends a continual stream of images to the server. The default recording resolution is set to 1280 x 720 and the frame rate to 25 FPS.

The recording is done using the `picamera` package that provides pure Python interface to the Raspberry Pi camera. If you are using the `Rasbian OS` then `picamera` should be already installed. To check, you can start python and try to import picamera:

```sh
python -c "import picamera"
```

If `picamera` is not installed, you can simply install it using the apt tool:

```sh
sudo apt-get update
sudo apt-get install python-picamera python3-picamera
```

Check [picamera](https://picamera.readthedocs.io/en/release-1.13/install.html) for more information.

### 2.1. Getting started
Connect your camera module to the CSI port on your Raspberry Pi; this is the long thin port adjacent to the HDMI socket. Gently lift the collar on top of the CSI port (if it comes off, don’t worry, you can push it back in but try to be more gentle in future!). Slide the ribbon cable of the camera module into the port with the blue side facing the Ethernet port (or where the Ethernet port would be if you’ve got a model A/A+).

Once the cable is seated in the port, press the collar back down to lock the cable in place. If done properly you should be able to easily lift the Pi by the camera’s cable without it falling out. The following illustrations show a well-seated camera cable with the correct orientation:
![connection](good_connection.jpg)

### 2.2. Testing
Now, apply power to your Pi. Once booted, start the Raspberry Pi Configuration utility and enable the camera module:
![pi-config](enable_camera.webp)

You will need to reboot after doing this (but this is one-time setup, so you won’t need to do it again unless you re-install your operating system or switch SD cards). Once rebooted, start a terminal and try the following command:

```sh
raspistill -o image.jpg
```

If everything is working correctly, the camera should start, a preview from the camera should appear on the display and, after a 5-second delay it should capture an image (storing it as image.jpg) before shutting down the camera. Proceed to the Basic Recipes.

### 2.3. Recording to a network stream
Recording video to a stream is done using a file-like object created from a socket(). A continual stream of video frames will be sent, so that the recording can be simply dumped straight to the network socket. Firstly, the server side script which will read the video stream and pipe it to a media player for display. 

The PC acts as the server, waiting for a connection from the client (PI). When it accepts a connection, it starts streaming video over it. To enable the commutation between the PC and the PI, the IP address on both sides must be adapted. Follow the instruction to set a static IP address on [Windows](https://support.microsoft.com/en-us/windows/change-tcp-ip-settings-bd0a07af-15f5-cd6a-363f-ca2b6f391ace).

EXAMPLE to set the ip adresses:
On the server side (PC) go to setting > Ethernet > change adapter options > select Ethernet > Properties > select Internet Protocol Version 4 (TCP/IPv4). A window will pop up. Select: Use the following IP addresses: 192.168.10.19 and for the subnet mask: ...
On the PI side set the IP adress to 192.168.10.18
(todo explain this in a better way).
![ethernet](ethernet.PNG)
todo: adapt the ip adress on the image.

todo: screenshot the other side on the pi.

The file `server.py` must be run from the PC i.e. on which device the recorded video should be stored. To start listening to the client connection, run:

```sh
python server.py
```

The file `client.py` must be run on the PI side. It will connect to the network socket and start the recording:

```sh
python client.py
```

At that moment a new directory with the name of the time of recording session. The folder will contain two files. The video (`date@time.H264`) and the timestamp (`date@time.start_ts.txt`) of the first video frame.
The video file will be used in step `X` to perform the tracking using DLC. The text file will be used to synchronize the video with RFID data to accomplish the ID matching process.
The duration of the recording, the frame rate and resolution can be changed in the `client.py` script.
Default values are set to 24 hours, 25 fps, 1280x720 pixels.

    Note: while the recording session is on, you will probably notice several seconds of latency. This is normal and is because media players buffer several seconds to guard against unreliable network streams. 

[More information](https://picamera.readthedocs.io/en/release-1.13/recipes1.html#recording-to-a-network-stream)


# Stage II: Pose estimation and multi-animal tracking
To perform pose estimation, DeepLabCut (DLC) need to be installed. DLC is a toolbox for markerless pose estimation of animals performing various tasks. As long as you can see (label) what you want to track, you can use this toolbox, as it is animal and object agnostic. A short development and application summary can be found [here](https://deeplabcut.github.io/DeepLabCut). 

## Configuration
Install DeepLabCut by typing the following in your terminal:

```sh
# todo: add dlc in the dependcies!
pip install deeplabcut[gui,tf]==2.2
```

We chose the best model checkpoint with the best evaluation results for analyzing the videos. Once you have downloaded our project and having DLC installed, you can now use our trained network to analyze your own videos. We provide a Jupyter Notebook that runs DeepLabCut and demonstrate the necessary steps to use DeepLabCut. Additional, we provide demo data that can be used in the analysis and helpful to walk you through your own dataset. 

The project directory contains a configuration file called `dlc_config.yaml`. The file contains many important parameters of the project, and you might need to change only some of them. You can open it in any text editor (like atom, gedit, vim etc.). Relevant parameters including their description:

* `p-cutoff`: specifies the threshold of the likelihood and helps to distinguishing likely body parts from uncertain once.
* `batch_size`: specifies how many frames to process at once during inference.
* `dotsize`: specifies the marker size when plotting the labels in videos.

The parameter `individuals` are names of “individuals” in the annotation dataset. This is generic (e.g. mouse1, mouse2, etc.). These individuals are comprised of the same bodyparts. We trained the network on datasets with three animals. However, for inference, if you have a video with more or less animals, that is fine - you can have more or less animals during the video analysis and the network can find them without changing anything in the config file!

Please note that novel videos DO NOT need to be added to the `dlc_config.yaml`. You can simply have a folder elsewhere on your computer and pass the video folder (then it will analyze all videos of the specified type (i.e. videotype='.mp4'), or pass the path to the folder or exact video(s) you wish to analyze.

## Starting the analysis
If you want to analyze all videos in a folder:
```python
deeplabcut.analyze_videos('config.yaml', ['fullpath/videos/'], videotype='.mp4')
```

If you want to analyze specific video(s):
```python
deeplabcut.analyze_videos('config.yaml',['fullpath/videos/video1.avi','/videos/video2.avi'])
```

Analyzing hour-long videos may take a while, but the task can be conveniently broken down into the analysis of smaller video clips. Add the following code to the Jupyter Notebook:
```python
from deeplabcut.utils.auxfun_videos import VideoWriter

_, ext = os.path.splitext(video_path)
vid = VideoWriter(video_path)
clips = vid.split(n_splits=10)
deeplabcut.analyze_videos(config_path, clips, ext)
```
todo: test video without encoding the video. test with h264. For Tips on video re-encoding and preprocessing see: https://deeplabcut.github.io/DeepLabCut/docs/recipes/io.html

## output
h5
todo: dlc.export_model
## Technical (Hardware) Considerations

## Troubleshooting
If you have any issue running the analysis or finding the results, it is most likely because:
a) the path is wrong (check that that folder is correct).
b) the video ending is different (by default DLC looks for ‘.avi’ files), you can change what it looks for by changing video_type (e.g. to ‘.mp4’).












---
# Stage III: Animal identification and verification
At this stage, the DLC-generated individual initial-dummy IDs are matched with RFID readings, and each microchipped mouse is assigned its associated RFID tag. Both RFID and DeepLabCut detections are synchronized. Based on the overlap between the position of the RFID tags and the animal locations, predicted by DLC, each mouse will be then mapped to its associated RFID tag.

DeepLabCut detections consists of several keypoints for each mouse. In order to perform the ID-matching, each individual need a single representative annotation. Thus, the centroid (mean location) of essential body parts (shoulder, spine1 to spine4, and tailbase) will be computed. Hence, an overlapping within a frame occurs when the averaged RFID tag and the centroid of a mouse body parts generated by DeepLabCut are predicted in the same RFID reader region. The centroid will also be used as a parameter in the process of the correction of identity switches (See the parameter `correction_method` in [Usage](#usage)).

---
## Correcting of Switched Identities (CSI)
The swapping problem occurs when assembled body parts are formed into tracks for each individual across frames. When DeepLabCut stitches tracklets and keypoints have inadequate pose estimation for few frames, tracklets may be lined incorrectly across frames. DeepLabCut claims that there should be no identity switching, if we have a highly accurate position estimation in every frame.

In the inference stage, if videos are recorded under significantly different conditions from those used to train the model, analyzed videos may have a tracking interruption, leading to identity switching. Nevertheless, we developed a method that includes multiple solutions to solve the problem of identity switching. The method is optional and can be used in the inference stage (after video analysis). Our approach is based on two major mechanisms for fixing the identity switching and functions once the ID-matching procedure is accomplished and each mouse is assigned an RFID tag: 1) proceed frame by frame, mouse by mouse, and review the overlapping between the RFID and the DeepLabCut detection in the surrounding region of the RFID reader, 2) Predict the identity swapping based on a euclidean distance threshold value between a mouse DeepLabCut-detections in each two consecutive frames. However, we determined in our experiment setup that this distance is between 50 and 100 pixels if no swapping occurs. If the distance exceeds the threshold (default is set to 50 pixels) in particular frames, the correction mechanism is triggered and only those frames, rather than all frames, are reviewed for switching possibilities. This approach reduces the number of false positive corrections (where the correction occurs, but there was no identity swapping). These methods will also be used as a parameter in the process of the correction of identity switches (See the parameter `correction_method` in [Usage](#usage)).

---
## Usage
The scripts can be run by opening the command prompt (terminal) and executing the `main.py` file. To run the script with specified arguments, use the following optional flags followed with the associated arguments:
```python
python3 main.py -i input_files_directory -o output_directory -t length_time_interval -m correction_method -d minDistDiff_threshold -p plot_type -l likelihood_threshold
```

Replace the argument keywords with meaningful values. Arguments in square brackets are optional [-h] -i -o [-w] [-d] [-m] [-p] [-l].
Or just simply: 

```python
python3 main.py -i input_files_directory -o output_directory
```

A a brief explanation of each parameter and how to use it:

**input_files_directory:** The path to the directory that holds all required input data. In this directory there must exist three files:
- `mp4` or `H264` raw video file containing animal(s). # todo test multiple videos in the same folder
- `h5` file that is analyzed by DLC. The file is in a hierarchical data format and should contain the coords of all individuals across video frames.
- `CSV` file holding all RFID detections. The file must contain the animal tag name, position, timestamp of reading and the duration of each event.
- `txt` file that contains timestamp of the first video frame.

**output_directory**: The path to directory where all results will be stored.

**length_time_interval**: Length of the time interval in seconds (numerical). The RFID detections are divided into intervals that are necessary for the DLC-RFID procedure. An interval could contain several occurrences (RFID events). For each time interval, only one position for each RFID tag will be estimated (or no position if no readings occur within the interval). This will allow to have a unique and decent estimated tag position. Good values are between 0.5 and 2.0 seconds. Default is set to 1.0 second. Read the thesis for more details.

**correction_method**: Method used for fixing the identity switching. The methods function once the ID-matching procedure is accomplished and each mouse is assigned an RFID tag. There exists four methods (todo find bp of centroid and compare with other method):

- `bp_perFrame`: proceed frame by frame, mouse by mouse based on body parts.
- `centroid_perFrame`: proceed frame by frame, mouse by mouse based on the centroid.
- `bp_frameDistDiff`: Predict the identity swapping based on a euclidean distance threshold value between a mouse DeepLabCut-detections in each two consecutive frames (based on body parts).
- `centroid_frameDistDiff`: Predict the identity swapping based on a euclidean distance threshold value between a mouse DeepLabCut-detections in each two consecutive frames (based on centroid).
- `all` : (default) Performs all method and store the results in different folders. # todo: change the default to centroid!

**minDistDiff_threshold**: Minimum value used as a threshold for the correction methods `bp_frameDistDiff` and `centroid_frameDistDiff`.

**plot_type**: Determines which labels should be plotted on the video. Use `RFID` to only plot RFID annotation (big circles), `DLC_bp` for plotting only the body parts of the animals predicted by DLC (small circles) and `DLC_centroid` for plotting the centroid of the DLC keypoints predictions (rings). `all` will plot all mentioned annotations (set as default)
['RFID', 'DLC_bp', 'DLC_centroid', 'all']

**likelihood_threshold**: A threshold value used for filtering the DLC detections when calculating the centroid. Labels with likelihood lower than this value will be excluded. Default is set to 0.9.

---
## Getting help
For every function there is an associated help document that can be viewed by adding a `?` after the function name in case of using ipython/Jupyter notebook; example:

```python
match_id?
```

To exit this help screen, type `:q`. And in python or pythonw, use the `help` function:

```python
help(match_id)
```


---
## Examples/demo data
todo
Additional, we provide demo data that can be analyzed to 
walks you through your own dataset
---
## What you need to get started with the identification and CSI procedures:
- Video(s) containing mice (`mp4` or `H264`).
- A File contains the RFID detection (`CSV`).
- A file containing the starting timestamp of the video (`txt`)
- todo : install dlc

## What you DON’T need to get started:
No specific computer/cameras/videos are required
