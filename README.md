# ImpactCapture

A python program that plots imapact data alongside a slow-motion video of the impact.

# Procedure

### Linux (Ubuntu or Debian based)
* Ensure python is installed globally (v3.10, if possible)
```bash
sudo apt install python3 python3-venv python3-pip
```
* Create and activate a virtual environment
```python
python3 -m venv venv
source venv/bin/activate
```
* Install requirements
```python
pip install -r requirements.txt
```
* Run the program (make sure excel and video file are accessible)
```python
python3 SlowMoCurrentProgress.py
```

### Usage
* Clicking on the "frame" count at the bottom of the video allows you to input a keyframe to skip to
* Adjusted python file to always read from the first sheet in the selected Excel file.
