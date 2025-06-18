# Low Cost Mocap (for drones)

### An extention to a cheap open source motion capture system with improved tools and cameras

## Cameras 

 
## Dependencies

Install the pseyepy python library: [https://github.com/bensondaled/pseyepy](https://github.com/bensondaled/pseyepy)

install npm and yarn

## Runing the code

make virtual python enviroment using pipx https://pipx.pypa.io/stable/installation/

create a virtual environment using python3 -m venv path/to/venv.
Low-Cost-Mocap$ python3 -m venv computer_code/
Low-Cost-Mocap$ source computer_code/bin/activate

cd into `computer_code`

run install script

`bash install.sh`

open python virtual enviroment

`source venv/bin/activate`

install ffmpeg

From the computer_code directory Run `yarn install` to install node dependencies

Then run `yarn run dev` to start the webserver. You will be given a url view the frontend interface.

In another terminal window, run `./computer_code/venv/bin/python3 computer_code/api/index.py` to start the backend server. This is what receives the camera streams and does motion capture computations.

## Documentation

The documentation for this project is admittedly pretty lacking, if anyone would like to put type definitions in the Python code that would be amazing and probably go a long way to helping the readability of the code. Feel free to also use the [discussion](https://github.com/jyjblrd/Mocap-Drones/discussions) tab to ask questions.

My blog post has some more information about the drones & camera: [joshuabird.com/blog/post/mocap-drones](https://joshuabird.com/blog/post/mocap-drones)

## YouTube Video

Watch this for information about the project & a demo!
[https://youtu.be/0ql20JKrscQ?si=jkxyOe-iCG7fa5th](https://youtu.be/0ql20JKrscQ?si=jkxyOe-iCG7fa5th)
![](https://github.com/jyjblrd/Mocap-Drones/blob/main/images/thumbnail.png?raw=true)

## Architectural Diagram

![](https://github.com/jyjblrd/Mocap-Drones/blob/main/images/architecture.png?raw=true)
