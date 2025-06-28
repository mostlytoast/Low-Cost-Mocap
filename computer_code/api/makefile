compileCalib:
	pyinstaller cameraCalibGui.py --onefile --noconsole --clean --strip --hidden-import='scipy._cyutility'
compileApp:
	pyinstaller app.py --onefile --noconsole --clean --strip --hidden-import='scipy._cyutility'

    #  --upx-dir /path/to/upx 
runCalib:
	./dist/cameraCalibGui
runApp:
	./dist/app
size:
	echo "app" ; du -h dist/app ; echo "cameraCalibGui" ; du -h dist/cameraCalibGui