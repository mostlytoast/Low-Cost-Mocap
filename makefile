SHELL := /bin/bash
install:
	cd computer_code && chmod +x install.sh && ./install.sh && pwd && source venv/bin/activate
compileCalib:
	cd computer_code && source venv/bin/activate && cd api && pip install pyinstaller && pyinstaller cameraCalibGui.py --paths . --onefile  --noconsole --clean --strip --hidden-import='scipy._cyutility' --hidden-import='api.calibrationWidget'  --hidden-import='api.setupWidget' --hidden-import='api.style' --hidden-import='api.viewapp'
compileTracking:
	cd computer_code && source venv/bin/activate && cd api && pip install pyinstaller && pyinstaller app.py --paths . --onefile --noconsole --clean --strip --hidden-import='scipy._cyutility'

    #  --upx-dir /path/to/upx 
calib:
	./computer_code/venv/bin/python3 computer_code/api/cameraCalibGui.py
tracking:
	./computer_code/venv/bin/python3 computer_code/api/viewapp.py
calibEXE:
	cd computer_code/api/dist && ./cameraCalibGui
trackingEXE:
	cd computer_code/api/dist && ./app
size:
	echo "app" ; du -h dist/app ; echo "cameraCalibGui" ; du -h dist/cameraCalibGui | sort -h 