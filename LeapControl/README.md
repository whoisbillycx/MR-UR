# RoboticHuman-Robot Interaction

## Requirements

- Leap Motion SDK & Drivers
  - https://developer-archive.leapmotion.com/v2
  - the ./lib in this repo specifies windows drivers, please add your own if running Linux/Mac
- Custom URX Python Package from https://github.com/jkur/python-urx/tree/SW3.5/urx
  - Because the one from pip is not updated :(
- Python 2.7(conda activate py27) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
- python-tk
  - `sudo apt-get install python-tk1`
- Everything in `requirements.txt`

## Linux

sudo dpkg --install Leap-*-x64.deb

terminal 1: sudo leapd # start leap motion service

terminal 2: `python ./follow_hand_all_x.py` x refer to rotation axis position(only position)

the leap motion and pose should along the x-axis 



## Quick-start Guide
1. Make sure all the prerequisites are fulfilled
2. **On Linux:** Make sure Leap Motion Daemon is running `sudo leapd `
3. In two separate terminal sessions run:
   1. `python ./gesture_handler.py`
   2. `python ./follow_hand_all_all.py`




