TODO
- implement debug print instead of print 
    - and have debug prints for all action
- better code structure 
- combine both apps into one 
- figure out a state manager? 
- figure out virtual camera test system 
- better unit test cases
- have the camera itself be passed as an object to classes not the index to access it in a list? 

tracking app
- figure out why cameras not opening 
- figure out why repeated calibrations causes scene to bug out
  - looks like its applying new data on top of old data 
- get floor calibration to work correctly 

camera calib bugs
- camera auto caputure not work well 
- crashes sometimes (might be caused by issues with cameras disconnecting)
- have way to delete cameras marked red in list 
- have an icon to indicate the active camera in list 
- rename id variables to distinguish the system id and internal id