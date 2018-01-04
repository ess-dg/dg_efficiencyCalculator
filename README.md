Detector Efficiency Calculator
============

Python standalone application 
This is a project in the ESS ERIC in order to make available to the public a library, a GUI tool and a webpage using Francesco Piscitelli's analytical tools for the calculation of efficiency for detectors based on solid converters.

    Webapp:          https://detectorefficiencycalculator.herokuapp.com/
    ESS Wiki Page:   https://ess-ics.atlassian.net/wiki/display/DG/Detector+efficiency+calculator
    Jira Project:    https://jira.esss.lu.se/projects/DGEF/summary
    Repo:            https://github.com/DetectorEfficiencyCalculator/dg_efficiencyCalculator
    Calculation libraries: https://github.com/alvcarmona/neutronDetectorEffFunctions

Requisites
------------
Python3: I recommend using a virtual environment  https://virtualenv.pypa.io/en/stable/userguide/
QT5: You can find the installation instructions here http://doc.qt.io/qt-5/ 
tk: ( sudo apt-get install python3-tk )

Execution (Make sure to use python 3)
------------

Install dependencies:
```
pip install -r requirements.txt
```
You may encounter problems depending on the OS and python when installing pyqt5, if this happens, you should install
sip pyqt5 manually for the desired python in your machine

Run launch script:
```
python launch.py
```
Troubleshooting
------------

You may encounter problems depending on the OS and python when installing pyqt5, if this happens, you should install
sip pyqt5 manually for the desired python in your machine.

There are known problems with matplotlib's backend in Mac Os X (ImportError: Gtk*).
To solve this you should edit the file ".matplotlib/matplotlibrc" and add the line "backend: TkAgg"

Developed by Álvaro Carmona Básañez
