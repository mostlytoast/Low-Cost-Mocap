# Low Cost Mocap (for drones)

### An extention to a cheap open source motion capture system with improved tools and cameras

## Goal of project

This project was started to take an existing motion capture system made by [jyjblrd](https://github.com/jyjblrd/Low-Cost-Mocap) and improve it so it can become an easy to use and accessible system. Thus providing a low cost alternative for motion capture systems costing only a few hundred dollars, which is significantly cheaper to current commercial systems which can cost multiple thousands of dollars. The main use case for this system is at smaller schools and hobbyists that need motion tracking systems for robotics and research applications.
To achieve this many improvements were made to hardware and software which are detailed bellow.

## Cameras

<img src="https://raw.githubusercontent.com/mostlytoast/Low-Cost-Mocap/refs/heads/no-cv-sfm/images/arducamov9281caseasmexplosion-ezgif.com-video-to-gif-converter-2.gif"  width="60%"  style="display: block; margin-left: auto; margin-right: auto;"/>

In previous iterations of this system PlayStation Eye cameras were used which required heavy modifications. This is no longer the case with a new and improved 3d printed case for the Arducam OV9281 usb webcam.

## Camera calibration

Another improvement is a dedicated app for camera calibration which provides intuitive steps for how to setup a system, shown bellow.

<img src="https://raw.githubusercontent.com/mostlytoast/Low-Cost-Mocap/refs/heads/newGUI/computer_code/images/calibration%20app%20home%20page.png"  width="50%" /><img src="https://raw.githubusercontent.com/mostlytoast/Low-Cost-Mocap/refs/heads/newGUI/computer_code/images/calibration%20app%20calib%20page.png"  width="50%" />

On the left users add cameras they wish to use for their setup to the "added webcams" list using arrows or keyboard shortcuts. They can also select webcams and view a preview by clicking "Open Camera". Additionally settings can be edited and have an instant preview of their effects in the preview window. To the right is the camera calibration page where users can use a predetermined checkerboard to calibrate each camera. Once all cameras are calibrated the user can save the current configuration and use it with the tracking application.

## Tracking app

The previous JS GUI implementation was replaced with an improved more portable PyQt application. This reduced dependencies making the application more portable and have a smaller file size, as well as being more performant.

<img src="https://raw.githubusercontent.com/mostlytoast/Low-Cost-Mocap/refs/heads/newGUI/computer_code/images/trackingapp.gif"  width="60%" style="display: block; margin-left: auto; margin-right: auto;"/>

The application provides the user with a clutter free experience showing them only what they need to get the system working. This includes camera Controls for exposure and gain as well as calibration and setup options. Once a system has been calibrated the configuration can be saved to be used again.

## Dependencies

The only dependency required is Python 3.12. and has only been tested to be fully working on linux. Unfortunatly, on MacOS, only the camera calibration app works due to mac not fully supporting OpenGL. I plan on switching to a more universal graphics platform for future versions. Support for windows remains unimplemented as the videoSubsystem needs to be modified to support it.

## Running the code

In the project directory run the install script with make and then open python virtual environment if it does not automatically do so.

```
$ make install 
$ source venv/bin/activate
```

Then run either the calibration or tracking app by running `make calib` or `make tracking` respectively.

## Compile to binary

One of the main reasons for removing JavaScript from this project was so PyInstaller could be used to create a portable executable making the project more accessible to normal users. Currently the binary has to be compiled manually which can be done by running `make compileCalib` and then `make compileTracking` to generate the exe for each. The executable for each can be found in computer_code/api/dist and can be run using commands `make calibEXE` and then `make trackingEXE`.
    Currently work is being done to combine both of these programs into one application which would reduce file sizes for the installer.

## Other repositories used

For 3d viewport in the tracking application I used the [PyQt5 Mesh Viewer](https://github.com/zishun/pyqt-meshviewer) by [zishun](https://github.com/zishun/pyqt-meshviewer/commits?author=zishun) with some extra modifications to support more features like zoom, displaying grids, etc.

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
