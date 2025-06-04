
import subprocess

def listWebcams():
    result = (
        subprocess.run("v4l2-ctl --list-devices", shell=True, stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .split("\n")
    )
    if result[-1] == "":
        result.pop()
    return result


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

    diff = []
    # print("result_no_cam", result_no_cam)

    # print("result_with_cam", result_with_cam)
    s = set(result_no_cam)
    diff = [x for x in result_with_cam if x not in s]
    # for element in result_no_cam: #https://www.geeksforgeeks.org/python-difference-two-lists/
    #     if element not in result_with_cam:
    #         diff.append(element)
    output = (
        []
    )  # list of cameras and their name and id (id will change after this program so done use it for long )

    for i, line in enumerate(diff):
        if "\t" not in line:
            # camera name found
            # todo get error checking working
            # Extract the last number from the next line (device id)
            device_line = diff[i + 1]
            # Extract the device id from a line like '\t/dev/video4'
            device_id_str = get_id_from_v4l2(device_line)
            device_id = int(device_id_str)
            output.append([line, device_id])
            # should this include the id of the camera? this could change immediately after running this code

    return output


def get_id_from_v4l2(device_line):
    device_id_str = device_line.strip().split("/")[-1].replace("video", "")
    return int(device_id_str)


def get_id_from_name(name):
    """_summary_ find the device id for a given usb product and vendor id which can be found with v4l2-ctl --list-devices or listWebcams() used to determine the opencv id for cv.VideoCapture(id)
    Args:
        name (_str_): the name of camera with id info given by v4l2-ctl --list-devices or listWebcams()
    Example:
        get_id_from_name("Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)")
    """
    #
    #
    lines = listWebcams()
    # print(result)
    # output = result.stdout.decode('utf-8').strip()
    # lines = output.split('\n')
    # # if lines[-1] == '' :
    #     lines.pop()
    cameras = []
    for index, line in enumerate(lines):
        # print(line)
        # print(line.split(' ')[3].strip(":"))
        # Device_id = int(line.split(' ')[3].strip(":"))
        if name in line:
            cameras.append(get_id_from_v4l2(lines[index + 1]))
        # if 'Webcam' in line:
        # vendor_id = line.split(' ')[5].split(':')[0]
        # product_id = line.split(' ')[5].split(':')[1]
        # # print(vendor_id, ", ", product_id)
        # if vendor_id == '0c45' and product_id == '6366':
        #     webcam = line.split(':')[-1].strip()
        #     cameras.append(webcam)
    return cameras[0]
