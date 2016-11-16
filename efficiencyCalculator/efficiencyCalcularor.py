#!/usr/bin/env python
import os
import sys

import efftools
from PyQt4 import QtGui, QtCore, uic

base, form = uic.loadUiType("efficiencyMainwindow.ui")


class Window(base, form):
    def __init__(self,  parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)
        self.calculatePushButton.clicked.connect(lambda: self.calculate_efficiency())
        self.show()
        sys.exit(app.exec_())

    def calculate_efficiency(self):
        print ''
        print 'calculate'
        sys.stdout.write("Thickness of Substrate: ")
        print self.substrateSpinBox.value()
        sys.stdout.write("Thickness of B10: ")
        print self.BSpinBox.value()
        sys.stdout.write("N of blades: ")
        print self.bladeSpinBox.value()
        if self.geometricalARadioButton.isChecked():
            print "Geometrical Arrangement: Single Coated "
        else:
            print "Geometrical Arrangement: Double Coated "
        sys.stdout.write("Material of substrate: ")
        print self.materialComboBox.currentText()
        sys.stdout.write("Incident angle: ")
        print self.angleSpinBox.value()
        sys.stdout.write("Gas selected: ")
        print self.gasSelectorComboBox.currentText()
        sys.stdout.write("Pressure of gas: ")
        print self.pressureSpinBox.value()
        sys.stdout.write("Sigma of Neutron: ")
        print self.sigmaSpinBox.value()
        sys.stdout.write("Threshold of Neutron: ")
        print self.thresholdSpinBox.value()
        result = efftools.efficiency4boron(self.BSpinBox.value(), 3, 1.3, 3.9, 1.5, 0.04)
        totalEffResult=result[0][0]
        self.resultLabel.setText(str(totalEffResult*100)+'%')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    #initialize app's main controller
    #controller = MainController()
    Window()
