

import os
import sys
import Models.B10 as B10
import efftools
from PyQt4 import QtGui, QtCore, uic
import Models.Detector as Detector
import Models.Blade as Blade
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
import matplotlib.figure
import numpy
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import efficiencyCalculator


class detectorDialog( QtGui.QDialog):
    wavelengthList = []
    bladeList = []
    converters = {}

    def __init__(self, detector, parent = None):
        super(detectorDialog, self).__init__(parent)
        uic.loadUi("detectorform.ui", self)
        self.setWindowTitle("Detector configurator")
        self.nameLineEdit.setText(detector.name)
        self.angleSpinBox.setValue(detector.angle)
        self.thresholdSpinBox.setValue(detector.threshold)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.addWavelengthButton.clicked.connect(lambda: self.add_wavelength())
        self.addBladeButton.clicked.connect(lambda: self.add_blades())

    def detector(self):
        detector = Detector.Detector('')
        detector.name = str(self.nameLineEdit.text())
        detector.threshold = self.thresholdSpinBox.value()
        detector.angle = self.angleSpinBox.value()
        detector.wavelength = self.wavelengthList
        detector.blades = self.bladeList
        return detector

    def add_wavelength(self):
        self.wavelengthList.append([self.waveSpinBox.value(), self.percentSpinBox.value()])
        rowPosition = self.lambdaTableWidget.rowCount()
        self.lambdaTableWidget.insertRow(rowPosition)
        self.lambdaTableWidget.setItem(rowPosition, 0, QtGui.QTableWidgetItem(str(self.waveSpinBox.value())))
        self.lambdaTableWidget.setItem(rowPosition, 1, QtGui.QTableWidgetItem(str(self.percentSpinBox.value())))
        self.addWavelengthButton.setEnabled(False)

    def add_blades(self):
        if (self.tSpinBox.value() > 0) | (self.bsSpinBox.value() > 0):
            nb = self.nbspinBox.value()
            bs = self.bsSpinBox.value()
            ts = self.tSpinBox.value()
            sub = self.subSpinBox.value()
            for n in range(0, nb):
                blade = Blade.Blade(bs, ts, sub, 0)
                self.bladeList.append(blade)
                self.BladeTableWidget.insertRow(n)
                self.BladeTableWidget.setItem(n, 0, QtGui.QTableWidgetItem(str(n+1)))
                self.BladeTableWidget.setItem(n, 1, QtGui.QTableWidgetItem(str(bs)))
                self.BladeTableWidget.setItem(n, 2, QtGui.QTableWidgetItem(str(ts)))
                self.BladeTableWidget.setItem(n, 3, QtGui.QTableWidgetItem(str(sub)))
            self.addBladeButton.setEnabled(False)
        else:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Warning)
            msg.setText("Please set thickness")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            retval = msg.exec_()


    @staticmethod
    def getDetector(detector, parent=None):
        dialog = detectorDialog(detector, parent)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        result = dialog.exec_()
        detector = dialog.detector()
        return detector, result == QtGui.QDialog.Accepted
