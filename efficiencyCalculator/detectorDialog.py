

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

    def __init__(self, detector, action, parent = None):
        super(detectorDialog, self).__init__(parent)
        uic.loadUi("detectorDialogTab.ui", self)
        self.Boron = B10.B10()
        self.action = action
        self.detector = detector
        self.setWindowTitle("Detector configurator")
        self.detector.delete = False
        self.nameLineEdit.setText(detector.name)
        self.angleSpinBox.setValue(detector.angle)
        self.thresholdSpinBox.setValue(detector.threshold)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Add plots layouts
        self.bladeInfoFigure = matplotlib.figure.Figure()
        self.bladeInfoCanvas = FigureCanvas(self.bladeInfoFigure)
        self.bladePlotLayout.addWidget(self.bladeInfoCanvas)

        self.bladeEffFigure = matplotlib.figure.Figure()
        self.bladeEffCanvas = FigureCanvas(self.bladeEffFigure)
        self.bladeEfficiencyPlotLayout.addWidget(self.bladeEffCanvas)

        self.thickVsEffFigure = matplotlib.figure.Figure()
        self.thickVsEffCanvas = FigureCanvas(self.thickVsEffFigure)
        self.thickVsEffPlotLayout.addWidget(self.thickVsEffCanvas)

        self.waveVsEffFigure = matplotlib.figure.Figure()
        self.waveVsEffCanvas = FigureCanvas(self.waveVsEffFigure)
        self.waveVsEffPlotLayout.addWidget(self.waveVsEffCanvas)

        if self.action == 'create':
            self.deleteButton.setEnabled(False)
        # List widget update
        if len(self.detector.blades) > 0:
            self.addBladeButton.setEnabled(False)
            try:
                c = 0
                ax = self.bladeInfoFigure.add_subplot(111)
                ax.set_xlabel('Blade Number')
                ax.set_ylabel('Blade thickness')
                ax.set_ylim([0,8])
                ax.plot(0, 0)
                ax.plot(len(self.detector.blades)+1, 0)
                for b in self.detector.blades:
                    rowPosition = c
                    self.BladeTableWidget.insertRow(rowPosition)
                    # Note that the plot displayed is the backscattering thickness
                    ax.plot(c+1, b.backscatter, 'd', color='black')
                    self.BladeTableWidget.setItem(rowPosition, 0, QtGui.QTableWidgetItem('Blade N:'+str(c+1)))
                    self.BladeTableWidget.setItem(rowPosition, 1, QtGui.QTableWidgetItem(str(b.backscatter)))
                    self.BladeTableWidget.setItem(rowPosition, 2, QtGui.QTableWidgetItem(str(b.transmission)))
                    self.BladeTableWidget.setItem(rowPosition, 3, QtGui.QTableWidgetItem(str(b.substrate)))
                    c += 1
                ax.grid(True)
                self.bladeInfoCanvas.draw()
            except IndexError:
                print 'no blades'
        else:
            self.deleteBladeButton.setEnabled(False)
        if len(self.detector.wavelength) > 0:
            self.addWavelengthButton.setEnabled(False)
            try:
                c = 0
                for b in self.detector.wavelength:
                    rowPosition = c
                    self.lambdaTableWidget.insertRow(rowPosition)
                    self.lambdaTableWidget.setItem(rowPosition, 0, QtGui.QTableWidgetItem(str(b[0])))
                    self.lambdaTableWidget.setItem(rowPosition, 1, QtGui.QTableWidgetItem(str(b[1])))
                    c += 1
            except IndexError:
                print 'no wavelength'
        else:
            self.deleteWaveButton.setEnabled(False)
        #Button connections
        self.deleteWaveButton.clicked.connect(lambda: self.delete_wavelength())
        self.addBladeButton.clicked.connect(lambda: self.add_blades())
        self.addSingleBladeButton.clicked.connect(lambda: self.add_layer())
        self.addWavelengthButton.clicked.connect(lambda: self.add_wavelength())
        self.deleteBladeButton.clicked.connect(lambda: self.delete_blades())
        self.deleteButton.clicked.connect(lambda: self.delete_detector())
        self.calculateTotalEffButton.clicked.connect(lambda: self.calculate_total_efficiency())



    def returnDetector(self):
        self.detector.name = str(self.nameLineEdit.text())
        self.detector.threshold = self.thresholdSpinBox.value()
        self.detector.angle = self.angleSpinBox.value()
        return self.detector, self.action

    def add_wavelength(self):
        self.detector.wavelength.append([self.waveSpinBox.value(), self.percentSpinBox.value()])
        rowPosition = self.lambdaTableWidget.rowCount()
        self.lambdaTableWidget.insertRow(rowPosition)
        self.lambdaTableWidget.setItem(rowPosition, 0, QtGui.QTableWidgetItem(str(self.waveSpinBox.value())))
        self.lambdaTableWidget.setItem(rowPosition, 1, QtGui.QTableWidgetItem(str(self.percentSpinBox.value())))
        self.addWavelengthButton.setEnabled(False)
        self.deleteWaveButton.setEnabled(True)

    def delete_wavelength(self):
        self.detector.wavelength = []
        self.lambdaTableWidget.setRowCount(0)
        self.addWavelengthButton.setEnabled(True)
        self.deleteWaveButton.setEnabled(False)
        self.bladeEffFigure.clear()
        self.bladeEffCanvas.draw()
        self.totalEfflabel.setText('unknown')

    def add_blades(self):
        if self.bsSpinBox.value() > 0:
            nb = self.nbspinBox.value()
            bs = self.bsSpinBox.value()
            ts = self.bsSpinBox.value()
            sub = self.subSpinBox.value()
            ax = self.bladeInfoFigure.add_subplot(111)
            ax.set_xlabel('Blade Number')
            ax.set_ylabel('Blade thickness ($\mu$)')
            ax.set_ylim([0, 8])
            ax.plot(0, 0)
            ax.plot(nb+1,0)
            for n in range(0, nb):
                # Note that the plot displayed is the backscattering thickness
                ax.plot(n + 1, bs, 'd', color='black')
                blade = Blade.Blade(bs, ts, sub, 0)
                self.detector.blades.append(blade)
                self.BladeTableWidget.insertRow(n)
                self.BladeTableWidget.setItem(n, 0, QtGui.QTableWidgetItem(str(n+1)))
                self.BladeTableWidget.setItem(n, 1, QtGui.QTableWidgetItem(str(bs)))
                self.BladeTableWidget.setItem(n, 2, QtGui.QTableWidgetItem(str(sub)))
            ax.grid(True)
            self.bladeInfoCanvas.draw()
            self.addBladeButton.setEnabled(False)
            self.addSingleBladeButton.setEnabled(False)
            self.deleteBladeButton.setEnabled(True)
            self.detector.single = False
        else:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Warning)
            msg.setText("Please set thickness")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            retval = msg.exec_()

    def add_layer(self):
        bs =0
        ts=0
        if self.bsSingleSpinBox.value() > 0:

            ax = self.bladeInfoFigure.add_subplot(111)
            ax.set_xlabel('Blade Number')
            ax.set_ylabel('Blade thickness ($\mu$)')
            ax.set_ylim([0, 8])
            ax.plot(0, 0)

            if self.transRadioButton.isChecked():
                bs = self.bsSingleSpinBox.value()
                ax.plot(1, bs, 'd', color='black')
            else:
                ts = self.bsSpinBox.value()
                ax.plot(1, ts, 'd', color='black')
            nb = 1
            sub = self.subSpinBox.value()
            ax.plot(nb + 1, 0)
            blade = Blade.Blade(bs, ts, sub, 0)
            self.detector.blades.append(blade)
            self.BladeTableWidget.insertRow(0)
            self.BladeTableWidget.setItem(0, 0, QtGui.QTableWidgetItem(str(1)))
            self.BladeTableWidget.setItem(0, 1, QtGui.QTableWidgetItem(str(self.bsSingleSpinBox.value())))
            self.BladeTableWidget.setItem(0, 2, QtGui.QTableWidgetItem(str(sub)))
            ax.grid(True)
            self.bladeInfoCanvas.draw()
            self.addBladeButton.setEnabled(False)
            self.addSingleBladeButton.setEnabled(False)
            self.deleteBladeButton.setEnabled(True)
            self.detector.single = True
        else:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Warning)
            msg.setText("Please set thickness")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            retval = msg.exec_()

    def delete_blades(self):
        self.bladeInfoCanvas.figure.clear()
        self.bladeInfoCanvas.draw()
        self.detector.blades = []
        self.BladeTableWidget.setRowCount(0)
        self.addBladeButton.setEnabled(True)
        self.addSingleBladeButton.setEnabled(True)
        self.deleteBladeButton.setEnabled(False)
        self.bladeEffFigure.clear()
        self.bladeEffCanvas.draw()
        self.totalEfflabel.setText('unknown')

    def delete_detector(self):
        reply = QtGui.QMessageBox.question(self, 'delete', 'Are you sure you want to delete this detector?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.action = 'delete'
            self.accept()

    @staticmethod
    def getDetector(detector, action, parent=None):
        dialog = detectorDialog(detector, action, parent)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        result = dialog.exec_()
        detector, action = dialog.returnDetector()

        return detector, result == QtGui.QDialog.Accepted, action

    def calculate_total_efficiency(self):
        if len(self.detector.blades) >= 1:
            if len(self.detector.wavelength) >= 1:
                print ''
                print 'Boron multi-blade double coated calculation '
                ranges = self.Boron.ranges(self.thresholdSpinBox.value(), str(self.converterComboBox.currentText()))
                sigma = self.Boron.full_sigma_calculation(self.detector.wavelength, self.angleSpinBox.value())
                if self.detector.single:
                    result = efftools.efficiency4boron(self.detector.blades[0].backscatter, ranges[0], ranges[1],  ranges[2],  ranges[3], sigma)
                else:
                    result = efftools.data_samethick_vs_thickandnb_depth(sigma, ranges, self.detector.blades)
                thickVsEff = efftools.metadata_samethick_vs_thickandnb(sigma,ranges, len(self.detector.blades))
                self.thickVsEffFigure.clear()
                bx = self.thickVsEffFigure.add_subplot(111)
                bx.plot(thickVsEff[0], thickVsEff[1])
                bx.grid(True)
                bx.set_xlabel('Blade thickness')
                bx.set_ylabel('Blade efficiency (%)')
                line = bx.plot([self.detector.blades[0].backscatter, self.detector.blades[0].backscatter], [0, result[1]], '--')
                plt.setp(line, 'color', 'k', 'linewidth', 0.5)
                line2 = bx.plot([0, self.detector.blades[0].backscatter], [result[1], result[1]], '--')
                plt.setp(line2, 'color', 'k', 'linewidth', 0.5)
                self.thickVsEffCanvas.draw()
                self.waveVsEffFigure.clear()
                sigmalist = np.arange(0.0011, 20, 0.1)
                sigmaeq = []
                for sigma in sigmalist:
                    # transformation for meeting requirements of functions
                    sigma = [[sigma],]
                    sigmaeq.append(self.Boron.full_sigma_calculation(sigma, self.angleSpinBox.value()))
                y = efftools.metadata_samethick_vs_wave(sigmaeq, self.detector.blades[0].backscatter, ranges, len(self.detector.blades))
                self.waveVsEffFigure.clear()
                cx = self.waveVsEffFigure.add_subplot(111)
                cx.plot(sigmalist, y, color='g')
                cx.plot([self.detector.wavelength[0][0], self.detector.wavelength[0][0]], [0, result[1]], '--', color='k')
                cx.plot([0, self.detector.wavelength[0][0]], [result[1], result[1]], '--', color='k')
                cx.grid(True)
                cx.set_xlabel('Blade wavelength')
                cx.set_ylabel('Blade efficiency (%)')
                self.waveVsEffCanvas.draw()

               # self.plotTitleLAbel.setText('Multi blade plots')
               # self.figure.clf()
               # data = efftools.data_samethick_vs_thickandnb(sigma, ranges, [len(self.detector.blades)], self)
                self.bladeEffFigure.clear()
                self.totalEfflabel.setText('<html><head/><body><p><span style=" font-size:24pt; font-weight:600;">'+str(result[1]*100)[:4]+'%')
                ax = self.bladeEffFigure.add_subplot(111)
                ax.set_xlabel('Blade Number')
                ax.set_ylabel('Blade efficiency (%)')
                ax.set_ylim([0, (result[0][0][1]*100+1)])
                ax.set_xlim([0, len(result[0])+1])
                ax.plot(0, 0)
                ax.plot(0, len(result[0])+1)
               # ax.plot(nb + 1, 0)
                for n in range(0, len(result[0])):
                    # Note that the plot displayed is the backscattering thickness
                    ax.plot(n + 1, result[0][n][1]*100, 'o', color='red')
                    self.BladeTableWidget.setItem(n, 3, QtGui.QTableWidgetItem(str(result[0][n][1]*100)+'%'))
                ax.grid(True)
                self.bladeEffCanvas.draw()
            else:
                msg = QtGui.QMessageBox()
                msg.setIcon(QtGui.QMessageBox.Warning)
                msg.setText("Please add wavelength")
                msg.setStandardButtons(QtGui.QMessageBox.Ok)
                retval = msg.exec_()
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Warning)
        msg.setText("Please add blades")
        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        retval = msg.exec_()
