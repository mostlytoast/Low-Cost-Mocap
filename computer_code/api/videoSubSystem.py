import platform
import subprocess


def listWebcams():
    # TODO get alternative versions working for different operating systems
    output = []
    if platform.system().lower() == "linux":
        result = (
            subprocess.run(
                "v4l2-ctl --list-devices", shell=True, stdout=subprocess.PIPE
            )
            .stdout.decode("utf-8")
            .split("\n")
        )
        result = [i for i in result if i != '']
        
        for i, line in enumerate(result):
            if ("\t" not in line) and (i < len(result)-1) :
                # camera name found
                # todo get error checking working
                # Extract the last number from the next line (device id)
                device_line = result[i + 1]
                # Extract the device id from a line like '\t/dev/video4'
                device_id_str = get_id_from_v4l2(device_line)
                device_id = int(device_id_str)
                output.append([line, device_id])
                # should this include the id of the camera? this could change immediately after running this code
    #todo get working for macos 
    return output


def find_camera():
    """_summary_

    Returns:
        _type_: _description_
    """
    # print()
    input("remove camera and press enter to continue")
    result_no_cam = listWebcams()

    input("connect the camera and press enter to continue")
    result_with_cam = listWebcams()
    # todo make easier to use by having it wait for connect and disconnect instead of waiting for prompt
    # result_with_cam = listWebcams()
    # result_no_cam = []
    # input("remove camera")
    # while(True):
    #     result_no_cam = listWebcams()
    #     if result_no_cam != result_with_cam:
    #         break
    #     time.sleep(0.5)
    # input("reconnect camera camera")
    # while(True):
    #     third_result = listWebcams()
    #     if result_no_cam != third_result:
    #         break
    #     time.sleep(0.5)
    return [x for x in result_with_cam if x not in result_no_cam]



def get_id_from_v4l2(device_line):
    device_id_str = device_line.strip().split("/")[-1].replace("video", "")
    return int(device_id_str)


def get_id_from_name(name):
    """_summary_ find the device id for a given usb product and vendor id which can be found with v4l2-ctl --list-devices or listWebcams() used to determine the opencv id for cv.VideoCapture(id)
    Args:
        name (_str_): the name of camera with id info given by v4l2-ctl --list-devices or listWebcams() return -1 if cant find it 
    Example:
        get_id_from_name("Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)")
    """
    # TODO get alternative versions working for different operating systems
    lines = listWebcams()

    cameras = []
    for index, line in enumerate(lines):
        if name in line:
            cameras.append(line[1])

    if len(cameras) == 0 or  len(cameras) > 1:
        return -1
    return cameras[0]


def getResolution(camera_id):
    # TODO have to use v4l2 to get list of supported resolution that user can select from and return that resolution as 2 vars width height
    # command to use
    # TODO make this platform independent
    if platform.system().lower() == "linux":
        command = "v4l2-ctl -d /dev/video" + str(camera_id) + " --list-formats-ext"
        result = (
            subprocess.run(command, shell=True, stdout=subprocess.PIPE)
            .stdout.decode("utf-8")
            .split("\n")
        )
        if result[-1] == "":
            result.pop()
        resolutions = []
        for line in result:
            if "Size: Discrete" in line:
                parts = line.strip().split()
                if len(parts) >= 3:
                    size = parts[2]
                    if "x" in size:
                        w, h = size.split("x")
                        resolutions.append((int(w), int(h)))

        return resolutions
    return [(1920,1080)]
