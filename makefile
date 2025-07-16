install:
	cd computer_code && chmod +x install.sh && ./install.sh && source venv/bin/activate
compileCalib:
	cd computer_code && pyinstaller gui/cameraCalibGui.py --onefile  --noconsole --clean --strip --hidden-import='scipy._cyutility'
compileTracking:
	cd computer_code && pyinstaller gui/viewapp.py --onefile --noconsole --clean --strip --hidden-import='scipy._cyutility'

    #  --upx-dir /path/to/upx 
calib:
	computer_code/venv/bin/python computer_code/calibrun.py
tracking:
	PYTHONPATH=computer_code/ computer_code/venv/bin/python computer_code/gui/viewapp.py

calibEXE:
	cd computer_code/api && ./dist/cameraCalibGui
trackingEXE:
	cd computer_code/api && ./dist/app
size:
	echo "app" ; du -h dist/app ; echo "cameraCalibGui" ; du -h dist/cameraCalibGui | sort -h 
	