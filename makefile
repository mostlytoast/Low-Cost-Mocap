SHELL := /bin/bash
install:
	cd computer_code && chmod +x install.sh && ./install.sh && pwd && source venv/bin/activate
compileCalib:
	cd computer_code/api && ../venv/bin/pip install pyinstaller && ../venv/bin/python -c "import calibrationWidget; print('OK')" && ../venv/bin/pyinstaller cameraCalibGui.py --paths . --onefile  --noconsole --clean --strip --hidden-import='scipy._cyutility' 
compileTracking:
	cd computer_code/api && ../venv/bin/pip install pyinstaller && ../venv/bin/pyinstaller viewapp.py --paths . --onefile --noconsole --clean --strip --hidden-import='scipy._cyutility'
calib:
	./computer_code/venv/bin/python3 computer_code/api/cameraCalibGui.py
tracking:
	./computer_code/venv/bin/python3 computer_code/api/viewapp.py
calibEXE:
	cd computer_code/api/dist && ./cameraCalibGui
trackingEXE:
	cd computer_code/api/dist && ./viewapp
size:
	echo "viewapp" ; du -h dist/viewapp ; echo "cameraCalibGui" ; du -h dist/cameraCalibGui | sort -h 