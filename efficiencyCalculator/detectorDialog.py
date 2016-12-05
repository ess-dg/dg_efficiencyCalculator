

import os
import sys
import Models.B10 as B10
import efftools
from PyQt4 import QtGui, QtCore, uic
import Models.Detector as Detector
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
import matplotlib.figure
import numpy
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import efficiencyCalculator

class DateDialog( QtGui.QDialog):
    def __init__(self, parent = None):
        super(DateDialog, self).__init__(parent)

        layout =  QtGui.QVBoxLayout(self)

        # nice widget for editing the date
        self.datetime =  QtGui.QDateTimeEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime( QtCore.QDateTime.currentDateTime())
        layout.addWidget(self.datetime)

        # OK and Cancel buttons
        buttons =  QtGui.QDialogButtonBox( QtGui.QDialogButtonBox.Ok |  QtGui.QDialogButtonBox.Cancel,  QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # get current date and time from the dialog
    def dateTime(self):
        return self.datetime.dateTime()

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getDateTime(parent=None):
        dialog = DateDialog(parent)
        result = dialog.exec_()
        date = dialog.dateTime()
        return (date.date(), date.time(), result == QtGui.QDialog.Accepted)


class detectorDialog( QtGui.QDialog):
    def __init__(self, detector, parent = None):
        super(detectorDialog, self).__init__(parent)
        uic.loadUi("detectorform.ui", self)
        self.nameLineEdit.setText(detector.name)
        self.angleSpinBox.setValue(detector.angle)
        self.thresholdSpinBox.setValue(detector.threshold)
        # nice widget for editing the date
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    # get current date and time from the dialog
    def detector(self):
        detector = Detector.Detector('')
        detector.name = str(self.nameLineEdit.text())
        detector.threshold = self.thresholdSpinBox.value()
        detector.angle = self.angleSpinBox.value()
        return detector

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getDetector(detector, parent=None):
        dialog = detectorDialog(detector, parent)
        result = dialog.exec_()
        detector = dialog.detector()
        return (detector, result == QtGui.QDialog.Accepted)
