# IN PROGRESS -> CREATING A WIKI


# Table of Contents
[1. Abstract](#abstractintroduction)


# Abstract/Introduction
Locating and tracking moving objects and organisms in spatiotemporal data finds application in a wide variety research [4]. For instance, In the field of neuroscience, social interactions are analysed to provide insights into healthy and pathological cognitive and emotional processes [3]. To realize the location and tracking aspect of such tasks, there exist a variety of methods which can extract and process the necessary information from video data.

This project applies an end-to-end solution based on Deep Neural Networks (DNNs) with the help of DeepLabCut (DLC), a Python framework built on TensorFlow, to investigate its viability in the context of pose estimation and tracking of mice in two experimental setups, which solely rely on raw video data as input.

The experiment uses a single, low-cost camera to record multiple RFID-tagged mice in a cage equipped with RFID sensors. In each recording session, animals are recorded and tracked for about 24 hours, allowing for the capture of a diversity of social interactions and building the basis for social behavior studies. Though not required for tracking, the RFID data can be used to detect potential identity swaps made by the trained DNN as well as match the mice’s RFIDs to their location in video. The final model achieves a test error of 4.9 pixels, which is similar to the labelling variability between humans (5.2 pixels).

# Structure
We are interested in tracking and localizing various body parts and identify multiple identical-looking mice across a broad collection of behaviors. 


In this experiment, we provide a set of scripts that is simple to run, integrating the DeepLabCut toolbox with the RFID technology. The system, implemented in Python, is completely automated. Our scripts are divided into two main stages: Stage I: Pose estimation and multi-animal tracking using DLC, that is used for creating a model for pose estimation and multi-animal tracking, and Stage II: Mouse identification using RFID system. In the first stage, a pose estimation model is created, trained and evaluated. In the second stage, the RFID detections are used to replace DLC dummy IDs with their corresponding RFID tag. Furthermore, we provide a set of scripts for checking and re-matching the mice ID whenever a potential ID swap made by DLC has been detected.

Mice need to be microshipped


# Experimental setup

Use image: Experimental setup overview
Use image: social Interaction: workflow

# Data Acquisition
## Video Recording
If the user is want to analyse videos without any interest in distigush between them (no identification) then there is no need for the RFID system. Also there is no need for the RFID system if the animals does not look identical (diiferent coat color) and mice do not need to be microshipped with RFID tags.

If mice need to be identified, then it's required to use the RFID system. Thus, a syncrynisation between the the video and the RFID data is nececarry. The scripts in the directory `video_recording` provides this functionality. The `server.py` file must be run on the server side which is the computer recieving the video (Windows, Unix).  The `client.py` file should be run on the Raspberry pi which is connected to the camera.

# Installation
You can clone the scripts of ColonyRack package from GitHub by firing up the shell and typing:

> git clone ..

Alternatively, you can go to the Git repository and download the package manually.


# Help
Arguments in squere brackets are optional [-h] -i  -o  [-w] [-d] [-m] [-p] [-l]

# Examples/demo data

# Usage
The scripts can be run by openning the command prompt (terminal) and excuting the `main.py` file. Type the following to run the scripts with default parameters:
> python3 main.py -i  inputPath -o outputPath

Use the following flags followed with the associated arguments:
> python3 main.py -i  files_directory -o output_directory -w TIME_WINDOW_LENGTH -d minDistDiff_threshold  -m correction_method -p plot_type -l likelihood_threshold


## What you need to get started with the identification and CSI procedures:
- Video(s) containing mice (`mp4` or `H264`).
- A File contains the RFID detection (`CSV`).
- A file containig the starting timestamp of the video (`txt`)

- 
## What you DON’T need to get started:
no specific computer/cameras/videos are required
