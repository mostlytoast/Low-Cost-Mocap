
# Low Cost Mocap (for drones)

### An extention to a cheap open source motion capture system with improved tools and cameras

## Cameras

![img](https://github.com/mostlytoast/Low-Cost-Mocap/blob/no-cv-sfm/images/arducamov9281caseasmexplosion-ezgif.com-video-to-gif-converter-2.gif?raw=true)

In previous iterations of this system PlayStation Eye cameras were used which required heavy modifications. This is no longer the case with a new and improved 3d printed case for the Arducam OV9281 usb webcam.

## Camera calibration

Another improvement is a dedicated app for camera calibration which provides intuitive steps for how to setup a system, shown bellow.
    On the left users add cameras they wish to use for their setup to the "added webcams" list using arrows or keyboard shortcuts. They can also select webcams and view a preview by clicking "Open Camera". Additionally settings can be edited and have an instant preview of their effects in the preview window.

To the right is the camera calibration page where users can use a predetermined checkerboard to calibrate each camera. Once all cameras are calibrated the user can save the current configuration and use it with the tracking application 



<img src="https://raw.githubusercontent.com/mostlytoast/Low-Cost-Mocap/refs/heads/newGUI/computer_code/images/calibration%20app%20home%20page.png"  width="50%" /><img src="https://raw.githubusercontent.com/mostlytoast/Low-Cost-Mocap/refs/heads/newGUI/computer_code/images/calibration%20app%20calib%20page.png"  width="50%" />

## Tracking app


## Dependencies

install npm and yarn

## Runing the code

make virtual python environment using pipx https://pipx.pypa.io/stable/installation/

create a virtual environment using python3 -m venv path/to/venv.
Low-Cost-Mocap$ python3 -m venv computer_code/
Low-Cost-Mocap$ source computer_code/bin/activate

cd into `computer_code`

run install script

`bash install.sh`

open python virtual environment

`source venv/bin/activate`

install ffmpeg

From the computer_code directory Run `yarn install` to install node dependencies

Then run `yarn run dev` to start the webserver. You will be given a url view the frontend interface.

In another terminal window, run `./computer_code/venv/bin/python3 computer_code/api/index.py` to start the backend server. This is what receives the camera streams and does motion capture computations.

## other repositories used

For 3d viewing i used the [PyQt5 Mesh Viewer](https://github.com/zishun/pyqt-meshviewer) by [zishun](https://github.com/zishun/pyqt-meshviewer/commits?author=zishun) with some extra modifications to support more features like zoom, displaying grids, etc.

## Useful tools

if you plan on working on the UI for this project consider using [ PyQtInspect](https://github.com/JezaChen/PyQtInspect-Open) which is a very useful tool to debug potential layout bugs.

`./computer_code/venv/bin/python3  -m PyQtInspect --direct --multiprocess --show-pqi-stack --qt-support=pyqt5 --file computer_code/api/cameraCalibGui.py `

## Documentation

The documentation for this project is admittedly pretty lacking, if anyone would like to put type definitions in the Python code that would be amazing and probably go a long way to helping the readability of the code. Feel free to also use the [discussion](https://github.com/jyjblrd/Mocap-Drones/discussions) tab to ask questions.

My blog post has some more information about the drones & camera: [joshuabird.com/blog/post/mocap-drones](https://joshuabird.com/blog/post/mocap-drones)

## YouTube Video

Watch this for information about the project & a demo!
[https://youtu.be/0ql20JKrscQ?si=jkxyOe-iCG7fa5th](https://youtu.be/0ql20JKrscQ?si=jkxyOe-iCG7fa5th)
![](https://github.com/jyjblrd/Mocap-Drones/blob/main/images/thumbnail.png?raw=true)

## Architectural Diagram

![](https://github.com/jyjblrd/Mocap-Drones/blob/main/images/architecture.png?raw=true)
