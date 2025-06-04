# import the opencv library 
import cv2 
import videoSubSystem

# define a video capture object 
vid = cv2.VideoCapture(videoSubSystem.get_id_from_name("Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4):")) 
# vid = cv2.VideoCapture(0, cv2.CAP_DSHOW) # this is the magic!
vid.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))

vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

vid.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
print("Auto-exposure disabled:", vid.get(cv2.CAP_PROP_AUTO_EXPOSURE))

success = vid.set(cv2.CAP_PROP_EXPOSURE, 100)

print("Exposure set:", success, "Current exposure:", vid.get(cv2.CAP_PROP_EXPOSURE))
vid.set(cv2.CAP_PROP_GAIN, 0) #gain = [gain] * self.num_cameras
while(True): 
	
	# Capture the video frame 
	# by frame 
	ret, frame = vid.read() 

	# Display the resulting frame 
	cv2.imshow('frame', frame) 
	
	# the 'q' button is set as the 
	# quitting button you may use any 
	# desired button of your choice 
	if cv2.waitKey(1) & 0xFF == ord('q'): 
		break

# After the loop release the cap object 
vid.release() 
# Destroy all the windows 
cv2.destroyAllWindows() 
