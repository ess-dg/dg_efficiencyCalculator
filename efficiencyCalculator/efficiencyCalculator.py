#!/usr/bin/env python
import copy
import os
import sys

import matplotlib
import matplotlib.figure
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy
import numpy as np
from PyQt5 import QtGui, uic, QtWidgets

from neutron_detector_eff_functions import B10, Detector, efftools

from .detectorDialog import detectorDialog as detectorDialog

base, form = uic.loadUiType(os.path.dirname(os.path.abspath(__file__))+"/efficiencyMainwindow2.ui")


class Window(QtWidgets.QMainWindow):
    converters = {}
    plotlist = {}
    detectorList = []

    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi(os.path.dirname(os.path.abspath(__file__))+"/efficiencyMainwindow2.ui", self)
        self.setWindowTitle("Detector efficiency calculator")
        # init list of converter materials, load data and add to converter dict
        # self.setupUi(self)
        self.start_window()

    def converter_list(self):
        self.Boron = B10.B10()
        self.converters.update(self.Boron.configurations)

    def start_window(self):
        self.addButton.clicked.connect(lambda: self.create_detector())
        self.editButton.clicked.connect(lambda: self.edit_detector())
        self.duplicateButton.clicked.connect(lambda: self.duplicate_detector())
        self.importButton.clicked.connect(lambda: self.import_detector())
        self.detectorTableWidget.itemDoubleClicked.connect(lambda: self.edit_detector())
        self.show()

    def create_detector(self):
        detector = Detector.Detector('Detector ' + str(len(self.detectorList) + 1))
        detector = detectorDialog.getDetector(detector, 'create')
        if detector[1]:
            self.detectorList.append(detector[0])
            self.update_detector_list()

    def duplicate_detector(self):
        try:
            detector = copy.deepcopy(self.detectorList[self.detectorTableWidget.selectedIndexes()[0].row()])
            detector.name = 'Copy of' + detector.name
            self.detectorList.append(detector)
            self.update_detector_list()

        except IndexError:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Please select a detector of the list")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()

    def edit_detector(self):
        try:
            detector = detectorDialog.getDetector(
                self.detectorList[self.detectorTableWidget.selectedIndexes()[0].row()], 'edit')
            if detector[1]:
                if detector[2] == 'edit':
                    self.detectorList[self.detectorTableWidget.selectedIndexes()[0].row()] = detector[0]
                    self.update_detector_list()
                elif detector[2] == 'delete':
                    self.detectorList.pop(self.detectorTableWidget.selectedIndexes()[0].row())
                    self.update_detector_list()

        except IndexError:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Please select a detector of the list")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()

    def update_detector_list(self):
        self.detectorTableWidget.setRowCount(0)
        c = 0
        for d in self.detectorList:
            rowPosition = c
            self.detectorTableWidget.insertRow(rowPosition)
            if d.name is not None:
                self.detectorTableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(d.name)))
            if d.blades is not None:
                self.detectorTableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(len(d.blades))))
            if d.angle is not None:
                self.detectorTableWidget.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(d.angle)))
            if len(d.wavelength) is not 0:
                if len(d.wavelength) > 1:
                    self.detectorTableWidget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem('Polichromatic'))
                else:
                    self.detectorTableWidget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(d.wavelength[0][0])))
            if d.threshold is not None:
                self.detectorTableWidget.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(str(d.threshold)))
            c += 1

    def plotview(self):
        """Deprecated  This method is called when the plot button is pushed """
        if self.yAxisComboBox.currentText() == 'Efficiency':
            if self.xAxisComboBox.currentText() == 'Thickness':
                if self.varComboBox.currentText() == 'Number of blades':
                    if len(self.plotlist) < 1:
                        self.plotTitleLAbel.setText(
                            '<html><head/><body><p><span style=" font-size:14pt; font-weight:600;">Efficiency VS Thickness with different Number of blades</span></p></body></html>')
                        self.thresholdSpinBox.setEnabled(False)
                        self.converterComboBox.setEnabled(False)
                        self.angleSpinBox.setEnabled(False)
                        self.lambdaSpinBox.setEnabled(False)
                        self.BSpinBox.setEnabled(False)
                        self.xAxisComboBox.setEnabled(False)
                        self.yAxisComboBox.setEnabled(False)
                        self.varComboBox.setEnabled(False)
                    ranges = self.Boron.ranges(self.thresholdSpinBox.value(), str(self.converterComboBox.currentText()))
                    sigma = self.Boron.full_sigma_calculation([self.lambdaSpinBox.value()], self.angleSpinBox.value())
                    eff = efftools.mg_same_thick(sigma, ranges, self.BSpinBox.value(), self.bladeSpinBox.value())[0]
                    metadata = efftools.metadata_samethick_vs_thickandnb(sigma, ranges, self.bladeSpinBox.value())
                    newplot = {str(len(self.plotlist)): {
                        'thickness': self.BSpinBox.value(),
                        'nb': self.bladeSpinBox.value(),
                        'wavelength': self.lambdaSpinBox.value(),
                        'angle': self.angleSpinBox.value(),
                        'threshold': self.thresholdSpinBox.value(),
                        'eff': eff,
                        'meta': metadata}
                    }
                    self.add_new_plot(newplot)
                    # id = newplot.keys()[0]
                    self.plotlist.update(newplot)
                    self.plot_list('d (um)', 'Efficiency')
            elif self.xAxisComboBox.currentText() == 'Wavelength':
                if len(self.plotlist) < 1:
                    self.plotTitleLAbel.setText(
                        '<html><head/><body><p><span style=" font-size:14pt; font-weight:600;">Efficiency VS Thickness with different Number of blades</span></p></body></html>')
                    self.thresholdSpinBox.setEnabled(False)
                    self.converterComboBox.setEnabled(False)
                    self.angleSpinBox.setEnabled(False)
                    self.lambdaSpinBox.setEnabled(False)
                    self.BSpinBox.setEnabled(False)
                    self.xAxisComboBox.setEnabled(False)
                    self.yAxisComboBox.setEnabled(False)
                    self.varComboBox.setEnabled(False)
                ranges = self.Boron.ranges(self.thresholdSpinBox.value(), str(self.converterComboBox.currentText()))
                sigmalist = np.arange(0.0011, 20, 0.1)
                sigmaeq = []
                sigma = self.Boron.full_sigma_calculation([self.lambdaSpinBox.value()], self.angleSpinBox.value())
                eff = efftools.mg_same_thick(sigma, ranges, self.BSpinBox.value(), self.bladeSpinBox.value())[0]
                for sigma in sigmalist:
                    sigmaeq.append(self.Boron.full_sigma_calculation([sigma], self.angleSpinBox.value()))
                y = efftools.metadata_samethick_vs_wave(sigmaeq, self.BSpinBox.value(), ranges,
                                                        self.bladeSpinBox.value())
                metadata = [sigmalist, y]
                newplot = {str(len(self.plotlist)): {
                    'thickness': self.BSpinBox.value(),
                    'nb': self.bladeSpinBox.value(),
                    'wavelength': self.lambdaSpinBox.value(),
                    'angle': self.angleSpinBox.value(),
                    'threshold': self.thresholdSpinBox.value(),
                    'eff': eff,
                    'meta': metadata}
                }
                self.add_new_plot(newplot)
                # id = newplot.keys()[0]
                self.plotlist.update(newplot)
                self.plot_list('Wavelength', 'Efficiency')

    def calculate_efficiency(self):
        self.figure.clf()
        print ('')
        print ('calculate')
        sys.stdout.write("Thickness of Substrate: ")
        print (self.substrateTSpinBox.value() + self.substrateBSpinBox.value())
        sys.stdout.write("Thickness of B10: ")
        print (self.BSpinBox.value())
        sys.stdout.write("N of blades: ")
        print (self.bladeSpinBox.value())
        if self.geometricalARadioButton.isChecked():
            print ("Geometrical Arrangement: Single Coated ")
        else:
            print ("Geometrical Arrangement: Double Coated ")
        sys.stdout.write("Material of substrate: ")
        print (self.materialComboBox.currentText())
        sys.stdout.write("Incident angle: ")
        print (self.angleSpinBox.value())
        sys.stdout.write("Gas selected: ")
        print (self.gasSelectorComboBox.currentText())
        sys.stdout.write("Pressure of gas: ")
        print (self.pressureSpinBox.value())
        sys.stdout.write("Lambda of Neutron: ")
        print (self.lambdaSpinBox.value())
        sys.stdout.write("Threshold of Neutron: ")
        print (self.thresholdSpinBox.value())
        # Calculation celection logic
        if not self.geometricalARadioButton.isChecked():
            if self.bladeSpinBox.value() == 1:
                self.eff_boron_singleblade_doublecoated()
            elif self.bladeSpinBox.value() > 1:
                self.eff_boron_multiblade_doublecoated()

    def plot_list(self, xlabel, ylabel):
        ''' plot some random stuff '''

        # create an axis

        ax = self.figure.add_subplot(111)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        # discards the old graph
        # ax.hold(False)

        for plot in self.plotlist:
            data = self.plotlist.get(plot).get('meta')
            ax.plot(data[0], data[1], '-')
        # plot data

        # refresh canvas
        ax.grid(True)
        self.canvas.draw()

    def add_new_plot(self, newplot):
        """Deprecated"""
        key = newplot.keys()[0]
        self.plotlist.update(newplot)
        rowPosition = self.plotTableWidget.rowCount()
        self.plotTableWidget.insertRow(rowPosition)
        self.plotTableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(newplot.get(key).get('thickness'))))
        self.plotTableWidget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(newplot.get(key).get('nb'))))
        self.plotTableWidget.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(newplot.get(key).get('wavelength'))))
        self.plotTableWidget.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(str(newplot.get(key).get('angle'))))
        self.plotTableWidget.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(str(newplot.get(key).get('threshold'))))
        self.plotTableWidget.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(str(newplot.get(key).get('eff'))))
        self.plotTableWidget.setItem(rowPosition, 7,
                                     QtWidgets.QTableWidgetItem(str(max(newplot.get(key).get('meta')[1])[0])))

    def clear_plots(self):
        """Deprecated"""
        print ('clear plots')
        self.plotTableWidget.setRowCount(0)
        self.canvas.figure.clear()
        self.canvas.draw()
        self.plotlist = {}
        self.thresholdSpinBox.setEnabled(True)
        self.converterComboBox.setEnabled(True)
        self.angleSpinBox.setEnabled(True)
        self.lambdaSpinBox.setEnabled(True)
        self.BSpinBox.setEnabled(True)
        self.xAxisComboBox.setEnabled(True)
        self.yAxisComboBox.setEnabled(True)
        self.varComboBox.setEnabled(True)
        self.plotTitleLAbel.setText(
            '<html><head/><body><p><span style=" font-size:14pt; font-weight:600;">Nothing to plot</span></p></body></html>')

    def eff_boron_singleblade_doublecoated(self):
        """Deprecated"""
        print ('')
        print ('Boron single blade double coated calculation ')
        ranges = self.Boron.ranges(self.thresholdSpinBox.value(), str(self.converterComboBox.currentText()))
        sigma = self.Boron.full_sigma_calculation([self.lambdaSpinBox.value()], self.angleSpinBox.value())
        result = efftools.efficiency4boron(self.BSpinBox.value(), ranges[0], ranges[1], ranges[2], ranges[3], sigma)
        self.plotTitleLAbel.setText('Single blade plots')
        self.ra94ResultLabel.setText(str(ranges[0]))
        self.rli94ResultLabel.setText(str(ranges[1]))
        self.ra6ResultLabel.setText(str(ranges[2]))
        self.rli6ResultLabel.setText(str(ranges[3]))
        self.totalResultLabel.setText(str(result[0][0] * 100) + '%')
        self.bsResultLabel.setText(str(result[1][0] * 100) + '%')
        self.tResultLabel.setText(str(result[2][0] * 100) + '%')

    def eff_boron_multiblade_doublecoated(self):
        """Deprecated"""
        print ('')
        print ('Boron multi-blade double coated calculation ')
        ranges = self.Boron.ranges(self.thresholdSpinBox.value(), str(self.converterComboBox.currentText()))
        sigma = self.Boron.full_sigma_calculation([self.lambdaSpinBox.value()], self.angleSpinBox.value())
        # TODO add aluminium consideration
        result = efftools.mg_same_thick(sigma, ranges, self.BSpinBox.value(), self.bladeSpinBox.value())
        self.plotTitleLAbel.setText('Multi blade plots')
        self.figure.clf()
        data = efftools.data_samethick_vs_thickandnb(sigma, ranges, [self.bladeSpinBox.value()], self)

    def plotstoppingpower(self):
        '''deprecated'''
        figure1 = matplotlib.figure.Figure()
        names = ["IONIZ_Linkoping_Alpha06.txt", "IONIZ_Linkoping_Alpha94.txt", "IONIZ_Linkoping_Li06.txt",
                 "IONIZ_Linkoping_Li94.txt"]
        threshold = 200000
        x = 0
        for name in names:
            x, E1, E2 = numpy.loadtxt(fname=os.path.dirname(os.path.abspath(__file__)) + "/data/B10/" + name,
                                      unpack=True, skiprows=27)

            plt.figure(1)  # the first figure
            sp1 = self.figure.add_subplot(211)  # the first subplot in the first figure
            plt.title('Stopping power')
            plt.grid(True)
            plt.xlabel('x (um)')
            plt.ylabel('dE/dx (keV/um)')

            sp1.plot(x, E1, label=name)

            # setting scale of sp1's axis
            scale_x = 10000
            scale_y = 1
            ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / scale_x))
            ticks_y = ticker.FuncFormatter(lambda E1, pos: '{0:g}'.format(E1 / scale_y))
            sp1.xaxis.set_major_formatter(ticks_x)
            sp1.yaxis.set_major_formatter(ticks_y)

            sp2 = self.figure.add_subplot(212)  # the second figure (integral)
            integral = 0
            w = x[1] - x[0]
            c0 = 0
            for y in E1:
                if c0 != 0:
                    # interpolation of distance from previous point
                    # all points seem to be at the same distance!
                    w = x[c0] - x[c0 - 1]
                integral = integral + y * w
                c0 += 1
            print (name + ': ')
            print (integral)
            print()

            E3 = []
            c1 = 0
            # variable to check if it has found the threshold point
            thFound = False
            for a in x:
                area = 0
                c2 = 0
                c0 = 0
                w = x[1] - x[0]
                for s in range(0, c1):
                    if c0 != 0:
                        # interpolation of distance from previous point
                        w = x[c0] - x[c0 - 1]
                    area = area + E1[c2] * w
                    c2 += 1
                    c0 += 1
                localArea = integral - area
                # check if this is the threshold point
                if thFound == False:
                    if localArea <= threshold:
                        thFound = True
                        sp2.plot([a, a], [0, threshold], color='k', linestyle='--', linewidth=1)
                E3.append(localArea)
                c1 += 1
                plt.grid(True)
            maxX = sp2.plot(x, E3, label=name)

        scale_x2 = 10000
        scale_y2 = 1000
        ticks_x2 = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / scale_x2))
        ticks_y2 = ticker.FuncFormatter(lambda E3, pos: '{0:g}'.format(E3 / scale_y2))
        sp2.xaxis.set_major_formatter(ticks_x2)
        sp2.yaxis.set_major_formatter(ticks_y2)

        # now add the threshold line
        plt.subplot(211)
        # plt.legend()
        # plt.legend()
        self.canvas.draw_idle()

    def import_detector(self):
        try:
            print ("Import config")
            filepath, _filter = QtWidgets.QFileDialog.getOpenFileName(self, "Select Directory")
            detector = Detector.Detector.json_parser(filepath)
            detector = detectorDialog.getDetector(detector, 'edit')
            if detector[1]:
                if detector[2] == 'edit':
                    self.detectorList.append(detector[0])
                    self.update_detector_list()


        except IOError:
            print ("Path error")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # initialize app's main controller
    # controller = MainController()
    window = Window()
    sys.exit(app.exec_())
    print(sys.path)
