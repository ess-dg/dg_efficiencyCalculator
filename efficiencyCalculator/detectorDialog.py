

import os
import sys
import Models.B10 as B10
import efftools
from PyQt4 import QtGui, QtCore, uic
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
    def __init__(self, parent = None):
        super(detectorDialog, self).__init__(parent)
        uic.loadUi("detectorform.ui", self)

        # nice widget for editing the date


    # get current date and time from the dialog
    def dateTime(self):
        return 1

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getDateTime(parent=None):
        dialog = detectorDialog(parent)
        result = dialog.exec_()
        date = dialog.dateTime()
        return 1
