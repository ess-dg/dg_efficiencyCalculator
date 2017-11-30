============
Detector Efficiency Calculator
============

Python standalone application 
This is an internship project in the ESS ERIC in order to make available to the public a standalone tool and a webpage using Francesco Piscitelli's analytical tools for the calculation of detector efficiency.

    ESS Wiki Page:   https://ess-ics.atlassian.net/wiki/display/DG/Detector+efficiency+calculator
    Jira Project:    https://jira.esss.lu.se/projects/DGEF/summary
    Repo:            https://github.com/DetectorEfficiencyCalculator/dg_efficiencyCalculator

Uses code from the project B10 MathUtils in https://bitbucket.org/europeanspallationsource/dg_dgcode

Python 3
qt5 ( http://doc.qt.io/qt-5/ )
tk ( sudo apt-get install python3-tk )

Execution (Make sure to use python 3)
------------

Install dependencies:
pip install -r requirements.txt

You may encounter problems depending on the OS and python when installing pyqt5, if this happens, you should install
sip pyqt5 manually for the desired python in your machine

Run launch script:
python launch.py



Developed by Álvaro Carmona Básañez