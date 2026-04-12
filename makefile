SHELL := /bin/bash
install:
	cd computer_code && chmod +x install.sh && ./install.sh && pwd && source venv/bin/activate
compileCalib:
	cd computer_code && ../venv/bin/pip install pyinstaller && ../venv/bin/python -c "import calibrationWidget; print('OK')" && ../venv/bin/pyinstaller cameraCalibGcomputer_code.Ui.py --paths . --onefile  --noconsole --clean --strip --hidden-import='scipy._cyutility' 
compileTracking:
	cd computer_code && ../venv/bin/pip install pyinstaller && ../venv/bin/pyinstaller trackingGui.py --paths . --onefile --noconsole --clean --strip --hidden-import='scipy._cyutility'
calib:
	./computer_code/venv/bin/python3 -m computer_code.Ui.cameraCalibGui
tracking:
	./computer_code/venv/bin/python3 -m computer_code.Ui.trackingGui
calibEXE:
	cd computer_code/dist && ./cameraCalibGui
trackingEXE:
	cd computer_code/dist && ./trackingGui
size:
	echo "trackingGui" ; du -h dist/trackingGui ; echo "cameraCalibGui" ; du -h dist/cameraCalibGui | sort -h 