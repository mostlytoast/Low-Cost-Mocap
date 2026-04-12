import platform
import subprocess
import re

def get_id_from_v4l2(device_line):
    match = re.search(r"/dev/video(\d+)", device_line)
    return match.group(1) if match else None


def listWebcams():
    """_summary_ returns list of attached webcams plus their ids
    Returns:
    list : [<system name>, device_id]
    """
    output = []
    system = platform.system().lower()

    if system == "linux":
        result = (
            subprocess.run(
                "v4l2-ctl --list-devices",
                shell=True,
                stdout=subprocess.PIPE,
            )
            .stdout.decode("utf-8")
            .split("\n")
        )
        result = [i for i in result if i != ""]

        for i, line in enumerate(result):
            if ("\t" not in line) and (i < len(result) - 1):
                device_line = result[i + 1]
                device_id_str = get_id_from_v4l2(device_line)

                if device_id_str is not None:
                    device_id = int(device_id_str)
                    output.append([line.strip(), device_id])

        # Sort by device_id to keep consistent ordering
        output.sort(key=lambda x: x[1])

    elif system == "darwin":  # macOS
        result = (
            subprocess.run(
                ["system_profiler", "SPCameraDataType"],
                stdout=subprocess.PIPE,
            )
            .stdout.decode("utf-8")
        )

        cameras = []
        current_name = None
        unique_id = None

        for line in result.split("\n"):
            line = line.strip()

            # Camera name (no indentation level marker like Linux, but ends with ":")
            if line.endswith(":") and "Model ID" not in line:
                current_name = line.replace(":", "")
                unique_id = None

            # Extract a stable identifier (UID)
            if "Unique ID:" in line:
                unique_id = line.split("Unique ID:")[-1].strip()
                print(current_name, unique_id)
            if current_name and unique_id:
                cameras.append((current_name, unique_id))
                current_name = None
                unique_id = None

        # Sort by unique_id to keep stable ordering across runs
        cameras.sort(key=lambda x: x[1])

        # Assign stable indices
        for idx, (name, uid) in enumerate(cameras):
            output.append([f"{name}, {uid}", idx])

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

    if len(cameras) == 0 or len(cameras) > 1:
        return -1
    return cameras[0]


def getResolution(camera_id):
    """gets resolutions available for specified camera 

    Args:
        camera_id (int): system id of camera 

    Returns:
        list (tuple) : list of tuples with width and then height 
    """
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
        # Remove duplicates
        resolutions = list(set(resolutions))
        resolutions.sort()
        return resolutions
    return [(1920, 1080)]
def getSettings(camera_id):
    """returns low lying information about a camera such as max min exposure and auto_exposure settings for manual and auto

    Args:
        camera_id (int): system id of camera 

    Returns:
        dict: dictionary containing max min exposure and auto_exposure settings for manual and auto 
        "manual_mode" : manual_mode,
            "auto_exposure_mode": auto_exposure_mode,
            "min_exposure": exposure_min,
            "max_exposure": exposure_max
    """
    if platform.system().lower() == "linux":
        command = "v4l2-ctl --all --device /dev/video" + str(camera_id) 
        result = (
            subprocess.run(command, shell=True, stdout=subprocess.PIPE)
            .stdout.decode("utf-8")
            .split("\n")
        )
        if result[-1] == "":
            result.pop()
        # Parse auto_exposure modes
        # auto_exposure_modes = {}
        manual_mode = auto_exposure_mode = None
        exposure_min = exposure_max = None
        for line in result:
            if "Manual Mode" in line:
                mode_match = re.match(r"\s*(\d+):", line)
                if mode_match:
                    mode_id = int(mode_match.group(1))
                    manual_mode = mode_id
            if "Aperture Priority Mode" in line:
                mode_match = re.match(r"\s*(\d+):", line)
                if mode_match:
                    mode_id = int(mode_match.group(1))
                    auto_exposure_mode = mode_id
            if "exposure_time_absolute" in line:
                min_match = re.search(r"min=(\d+)", line)
                max_match = re.search(r"max=(\d+)", line)
                if min_match and max_match:
                    exposure_min = int(min_match.group(1))
                    exposure_max = int(max_match.group(1))
                break
        # TODO have it return current exposure to and then use that to set the data fields 
        # Example return structure
        return {
            "manual_mode" : manual_mode,
            "auto_exposure_mode": auto_exposure_mode,
            # todo seams that everything defaults to 1 to 100
            "min_exposure": 1,
            "max_exposure": 100
        }
    return {
        "manual_mode" : 0,
        "auto_exposure_mode": 0,
        # todo seams that everything defaults to 1 to 100
        "min_exposure": 1,
        "max_exposure": 100
    }

if __name__ == "__main__":
    print("test")
    print(getSettings(get_id_from_name("Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.1.1):")))