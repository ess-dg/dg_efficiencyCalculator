# -*- coding: utf-8 -*-
import matplotlib
import matplotlib.figure
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtGui, QtCore, uic, QtWidgets
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from random import randint

from .Models import B10
from .Models import Blade as Blade
from .Models import efftools


class detectorDialog( QtWidgets.QDialog):

    def __init__(self, detector, action, parent = None):
        super(detectorDialog, self).__init__(parent)
        uic.loadUi(os.path.dirname(os.path.abspath(__file__))+"/detectorDialogTab.ui", self)

        self.state = 'venv'
        self.Boron = B10.B10()
        self.action = action
        self.detector = detector
        self.setWindowTitle("Detector configurator")
        if detector.converterConfiguration != '':
            if detector.converterConfiguration is not None:
                index = self.converterComboBox.findText(detector.converterConfiguration)
                self.converterComboBox.setCurrentIndex(index)
        self.detector.delete = False
        self.nameLineEdit.setText(detector.name)
        self.angleSpinBox.setValue(detector.angle)
        self.thresholdSpinBox.setValue(detector.threshold)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.waveTabWidget.hide()
        self.waveFormWidget.show()
        self.effWidget.hide()
        self.bladeTabWidget.show()
        self.bladePlotWidget.hide()
        self.thickVsEff = []
        # Add plots layouts
        self.waveInfoFigure = matplotlib.figure.Figure()
        self.waveInfoCanvas = FigureCanvas(self.waveInfoFigure)
        self.wavePlotLayout.addWidget(self.waveInfoCanvas)
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

        #Interaction plot toolbars
        self.toolbar = NavigationToolbar(self.thickVsEffCanvas, self)
        self.toolbar2 = NavigationToolbar(self.waveVsEffCanvas, self)
        self.toolbar3 = NavigationToolbar(self.bladeEffCanvas, self)
        self.toolbar4 = NavigationToolbar(self.bladeInfoCanvas, self)
        self.toolbar5 = NavigationToolbar(self.waveInfoCanvas, self)
        self.thickToolLayout.addWidget(self.toolbar)
        self.waveToolLayout.addWidget(self.toolbar2)
        self.wavePlotLayout.addWidget(self.toolbar5)
        self.bladetoolPlotLayout.addWidget(self.toolbar4)
        self.effPlotHorizontalLayout.addWidget(self.toolbar3)


        self.BladeTableWidget.setColumnWidth(0, 70)
        self.BladeTableWidget.setColumnWidth(1, 85)
        self.BladeTableWidget.setColumnWidth(2, 115)
        self.BladeTableWidget.setColumnWidth(3, 75)

        self.verticalLayout_8.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.verticalLayout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)



        # self.toolbar.hide()
        if self.action == 'create':
            self.deleteButton.setEnabled(False)
        # List widget update
        if len(self.detector.blades) > 0:
            print ('loading blade')
            self.addBladeButton.setEnabled(False)
            try:
                c = 0
                ax = self.bladeInfoFigure.add_subplot(111)
                ax.set_xlabel('Depth')
                ax.set_ylabel('Blade thickness (micron)')
                ax.set_ylim([0,8])
                ax.plot(0, 0)
                ax.plot(len(self.detector.blades)+1, 0)
                for b in self.detector.blades:
                    rowPosition = c

                    self.BladeTableWidget.insertRow(rowPosition)
                    # Note that the plot displayed is the backscattering thickness
                    ax.plot(c+1, b.backscatter, 'd', color='black')

                    item = QtWidgets.QTableWidgetItem('Blade N:'+str(c+1))
                    # execute the line below to every item you need locked
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

                    self.BladeTableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(item))

                    item = QtWidgets.QTableWidgetItem(str(b.backscatter))
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                    self.BladeTableWidget.setItem(rowPosition, 1, item)

                  #  self.BladeTableWidget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(b.transmission)))

                    item = QtWidgets.QTableWidgetItem(str(b.substrate))
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                    self.BladeTableWidget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(item))

                    item = QtWidgets.QTableWidgetItem('unknown')
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.BladeTableWidget.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(item))
                    c += 1
                ax.grid(True)
                if self.detector.single:
                    self.bladeClassLabel.setText("Single coated blade")
                else:
                    self.bladeClassLabel.setText("Multigrid with " + str(len(self.detector.blades)) + " blades")
                self.effWidget.show()
                self.bladePlotWidget.show()
                self.bladeTabWidget.hide()
                self.bladeInfoCanvas.draw()
            except IndexError:
                print ('no blades')
        else:
            self.deleteBladeButton.setEnabled(False)
        if len(self.detector.wavelength) > 0:
            print ('loading wavelength')
            try:
                c = 0
                self.waveTabWidget.show()
                self.waveFormWidget.hide()
                if len(self.detector.wavelength) > 1:
                    ax = self.waveInfoFigure.add_subplot(111)
                    ax.set_xlabel('Wavelength (Angstrom)')
                    ax.set_ylabel('weight (%)')
                    # ax.set_xlim([0, len(wave)])
                    # a = [[1, 2], [3, 3], [4, 4], [5, 2]]
                    # ax.plot(a, 'ro')
                    # ax.plot(wave)
                    ax.plot(self.detector.wavelength, color='b')
                    ax.grid()
                else:
                    ax = self.waveInfoFigure.add_subplot(111)
                    ax.set_xlabel('Wavelength (Angstrom)')
                    ax.set_ylabel('weight (%)')
                    # a = [[1, 2], [3, 3], [4, 4], [5, 2]]
                    # ax.plot(a, 'ro')
                    # ax.plot(wave)
                    x = self.wavePoliSpinBox.value()
                    y = self.percentPoliSpinBox.value()
                    ax.plot([x, x], [0, 100], color='b')
                    ax.set_xlim([0, x + x])
                    ax.grid()
                for b in self.detector.wavelength:
                    rowPosition = c
                    self.lambdaTableWidget.insertRow(rowPosition)
                    self.lambdaTableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(b[0])))
                    self.lambdaTableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(b[1])))
                    c += 1
            except IndexError:
                print ('no wavelength')
        else:
            self.deleteWaveButton.setEnabled(False)
        #Button connections
        self.deleteWaveButton.clicked.connect(lambda: self.delete_wavelength())
        self.addBladeButton.clicked.connect(lambda: self.add_blades())
        self.addSingleBladeButton.clicked.connect(lambda: self.add_layer())
        self.addPoliWavelengthButton.clicked.connect(lambda: self.add_poli_wavelength())
        self.deleteBladeButton.clicked.connect(lambda: self.delete_blades())
        self.deleteButton.clicked.connect(lambda: self.delete_detector())
        self.calculateTotalEffButton.clicked.connect(lambda: self.calculate_total_efficiency())
        self.optimizeThicknessSameButton.clicked.connect(lambda: self.optimize_thickness_same())
        self.optimizeThicknessDiffButton.clicked.connect(lambda: self.optimize_thickness_diff())
        self.exportButton.clicked.connect(lambda: self.export())
        self.exportThickvseffButton.clicked.connect(lambda: self.export_plot_file('effvsthick'))
        self.exportEffVsDepthButton.clicked.connect(lambda: self.export_plot_file('effvsdepth'))
        self.exportEffVsWaveButton.clicked.connect(lambda: self.export_plot_file('effVsWave'))
        self.nameLineEdit.textChanged.connect(lambda: self.updateDetector())
        self.importWaveButton.clicked.connect(lambda: self.importWave())
        self.exportThickDepthButton.clicked.connect(lambda: self.export_plot_file('thickDepth'))


        #table edit signal

        self.BladeTableWidget.itemChanged.connect(self.tableEdited)

        #Button disable
        self.exportButton.setEnabled(False)
        self.calculateTotalEffButton.setDefault(True)
        self.exportThickvseffButton.setEnabled(False)
        self.exportEffVsWaveButton.setEnabled(False)
        self.optimizeThicknessDiffButton.setEnabled(False)
        #validation for name line edit
        reg_ex = QtCore.QRegExp("[A-Za-z0-9_]{0,255}")
        name_validator = QtGui.QRegExpValidator(reg_ex, self.nameLineEdit)
        self.nameLineEdit.setValidator(name_validator)

    def updateDetector(self):
        print ('parameter changed')
        self.detector.converterConfiguration = str(self.converterComboBox.currentText())
        self.detector.name = str(self.nameLineEdit.text())
        self.detector.threshold = self.thresholdSpinBox.value()
        self.detector.angle = self.angleSpinBox.value()

    def returnDetector(self):
        self.detector.name = str(self.nameLineEdit.text())
        self.detector.threshold = self.thresholdSpinBox.value()
        self.detector.angle = self.angleSpinBox.value()
        self.detector.converterConfiguration = str(self.converterComboBox.currentText())
        return self.detector, self.action

    def add_wavelength(self):
        """
        Deprecated
        """
        print ('add wavelength')
        self.waveTabWidget.show()
        self.waveFormWidget.hide()
        self.detector.wavelength.append([self.waveSpinBox.value(), self.percentSpinBox.value()])
        rowPosition = self.lambdaTableWidget.rowCount()
        self.lambdaTableWidget.insertRow(rowPosition)
        self.lambdaTableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(self.waveSpinBox.value())))
        self.lambdaTableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(self.percentSpinBox.value())))
        self.deleteWaveButton.setEnabled(True)

    def add_poli_wavelength(self):
        """
        adds a wavelength with lambda and % and plots it
        """
        print ('add wavelength')
        self.detector.wavelength.append([self.wavePoliSpinBox.value(), self.percentPoliSpinBox.value()])
        rowPosition = self.lambdaTableWidget.rowCount()
        self.lambdaTableWidget.insertRow(rowPosition)
        self.lambdaTableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(self.wavePoliSpinBox.value())))
        self.lambdaTableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(self.percentPoliSpinBox.value())))
        self.percentPoliSpinBox.setMaximum(self.percentPoliSpinBox.maximum() - self.percentPoliSpinBox.value())
        # self.addPoliWavelengthButton.setEnabled(False)
        self.deleteWaveButton.setEnabled(True)
        self.waveTabWidget.show()
        ax = self.waveInfoFigure.add_subplot(111)
        ax.set_xlabel('Wavelength (angstrom)')
        ax.set_ylabel('weight (%)')
        # a = [[1, 2], [3, 3], [4, 4], [5, 2]]
        # ax.plot(a, 'ro')
        # ax.plot(wave)
        x = self.wavePoliSpinBox.value()
        y = self.percentPoliSpinBox.value()
        ax.plot([x, x],[0,100], color='b')
        ax.set_xlim([0, x+x])
        ax.grid()
        if self.percentPoliSpinBox.maximum() == 0:
            self.waveFormWidget.hide()
            self.addPoliWavelengthButton.setEnabled(False)

    def delete_wavelength(self):
        """
        Deletes all wavelengths from current configuration
        """
        print ('clear wavelength')
        self.waveInfoFigure.clear()
        self.waveTabWidget.hide()
        self.waveFormWidget.show()
        self.detector.wavelength = []
        self.lambdaTableWidget.setRowCount(0)
        self.addPoliWavelengthButton.setEnabled(True)
        self.deleteWaveButton.setEnabled(False)
        self.bladeEffFigure.clear()
        self.bladeEffCanvas.draw()
        self.totalEfflabel.setText('unknown')
        self.percentPoliSpinBox.setMaximum(100)
        self.percentPoliSpinBox.setValue(100)

    def refresh_blades(self):
        """
        Updates blade list and plots to current configuration
        """
        print ('Refresh blade list and plot')
        self.state = 'RefressB'
        self.bladeInfoFigure.clear()
        ax = self.bladeInfoFigure.add_subplot(111)
        ax.set_xlabel('Depth')
        ax.set_ylabel('Blade thickness ($\mu$)')
        ax.set_ylim([0, 8])
        ax.plot(0, 0)
        nb = len(self.detector.blades)
        ax.plot(nb + 1, 0)
        sub = self.detector.blades[0].substrate
        for n in range(0, nb):
            # Note that the plot displayed is the backscattering thickness
            bs = self.detector.blades[n].backscatter
            ax.plot(n + 1, bs, 'd', color='black')
            self.BladeTableWidget.setItem(n, 0, QtWidgets.QTableWidgetItem(str(n + 1)))
            self.BladeTableWidget.setItem(n, 1, QtWidgets.QTableWidgetItem(str(bs)))
            self.BladeTableWidget.setItem(n, 2, QtWidgets.QTableWidgetItem(str(sub)))
        ax.grid(True)
        self.bladeInfoCanvas.draw()
        self.state = ''

    def add_blades(self):
        """
        adds blades to configuration, updates blade list and plots
        """
        if self.bsSpinBox.value() > 0:
            print ('add blades to current configuration')
            self.effWidget.show()
            self.bladeTabWidget.hide()
            self.bladePlotWidget.show()
            self.state = 'AddB'
            self.tabWidget_2.setCurrentIndex(0)
            nb = self.nbspinBox.value()
            bs = self.bsSpinBox.value()
            ts = self.bsSpinBox.value()
            sub = self.subSpinBox.value()
            ax = self.bladeInfoFigure.add_subplot(111)
            ax.set_xlabel('Depth')
            ax.set_ylabel('Blade thickness ($\mu$)')
            ax.set_ylim([0, 8])
            ax.plot(0, 0)
            ax.plot(nb+1,0)
            self.bladeClassLabel.setText("Multigrid with " +str(nb)+ " blades")
            for n in range(0, nb):
                # Note that the plot displayed is the backscattering thickness
                ax.plot(n + 1, bs, 'd', color='black')
                blade = Blade.Blade(bs, ts, sub, 0)
                self.detector.blades.append(blade)
                self.BladeTableWidget.insertRow(n)
                self.BladeTableWidget.setItem(n, 0, QtWidgets.QTableWidgetItem(str(n+1)))
                item = QtWidgets.QTableWidgetItem(str(bs))
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                self.BladeTableWidget.setItem(n, 1, item)
                self.BladeTableWidget.setItem(n, 2, QtWidgets.QTableWidgetItem(str(sub)))
            ax.grid(True)
            self.bladeInfoCanvas.draw()
            self.addBladeButton.setEnabled(False)
            self.addSingleBladeButton.setEnabled(False)
            self.deleteBladeButton.setEnabled(True)
            self.detector.single = False
            self.state = ''
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Please set thickness")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            retval = msg.exec_()

    def add_layer(self):
        """
         adds single coated blade to configuration
        """
        self.state = 'addLayer'
        bs =0
        ts=0
        self.tabWidget_2.setCurrentIndex(0)
        self.bladeClassLabel.setText("Single coated blade")
        if self.bsSingleSpinBox.value() > 0:
            print ('Add single coated blade')
            self.effWidget.show()
            self.bladeTabWidget.hide()
            self.bladePlotWidget.show()
            ax = self.bladeInfoFigure.add_subplot(111)
            ax.set_xlabel('Depth')
            ax.set_ylabel('Blade thickness ($\mu$)')
            ax.set_ylim([0, 8])
            ax.plot(0, 0)
            bs = self.bsSingleSpinBox.value()
            ax.plot(1, bs, 'd', color='black')
            nb = 1
            sub = self.subSpinBox.value()
            ax.plot(nb + 1, 0)
            blade = Blade.Blade(bs, ts, sub, 0)
            self.detector.blades.append(blade)
            self.BladeTableWidget.insertRow(0)
            self.BladeTableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem(str(1)))
            self.BladeTableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem(str(self.bsSingleSpinBox.value())))
            self.BladeTableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem(str(sub)))
            ax.grid(True)
            self.bladeInfoCanvas.draw()
            self.addBladeButton.setEnabled(False)
            self.addSingleBladeButton.setEnabled(False)
            self.deleteBladeButton.setEnabled(True)
            self.detector.single = True
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Please set thickness")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            retval = msg.exec_()
        self.state = ''

    def delete_blades(self):
        """
        Clears blades from current configuration
        """
        print ('clear blades')
        self.effWidget.hide()
        self.bladeTabWidget.show()
        self.bladePlotWidget.hide()
        self.tabWidget_2.setCurrentIndex(0)
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
        reply = QtWidgets.QMessageBox.question(self, 'delete', 'Are you sure you want to delete this detector?', QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            print ('delete detector')
            self.action = 'delete'
            self.accept()

    @staticmethod
    def getDetector(detector, action, parent=None):
        dialog = detectorDialog(detector, action, parent)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        result = dialog.exec_()
        detector, action = dialog.returnDetector()
        print ('close dialog')
        return detector, result == QtWidgets.QDialog.Accepted, action

    def calculate_total_efficiency(self):
        self.detector.converterConfiguration = str(self.converterComboBox.currentText())
        print ('CalculateTotalEff')
        if len(self.detector.blades) >= 1:
            if len(self.detector.wavelength) >= 1:
                self.detector.angle = self.angleSpinBox.value()
                self.detector.threshold = self.thresholdSpinBox.value()
                ranges = self.Boron.ranges(self.thresholdSpinBox.value(), str(self.converterComboBox.currentText()))
                sigma = self.Boron.full_sigma_calculation(self.detector.wavelength, self.angleSpinBox.value())
                result = self.detector.calculate_eff()
                if self.detector.single:
                   # print 'Boron single layer calculation '
                    self.totalEfflabel.setText(
                        '<html><head/><body style=" font-size:24pt; font-weight:400;"><p>Backscattering: ' + str(result[0][0] * 100)[:4] + '% </p><p>Transmission: ' + str(result[1][0] * 100)[:4]+'</p>')
                    self.plot_blade_figure_single(result)
                else:
                   # print 'Boron multi-blade double coated calculation '
                    self.totalEfflabel.setText(
                        '<html><head/><body><p><span style=" font-size:24pt; font-weight:600;">' + str(result[1] * 100)[:4] + '%')
                    self.plot_blade_figure(result)
                self.plot_thick_vs_eff(sigma, ranges, self.detector.blades, result)

                if len(sigma) == 1:
                    self.waveVsEffFigure.clear()
                    sigmalist = np.arange(0.0011, 20, 0.1)
                    sigmaeq = []
                    for sigma in sigmalist:
                        # transformation for meeting requirements of functions
                        sigma = [[sigma],]
                        sigmaeq.append(self.Boron.full_sigma_calculation(sigma, self.angleSpinBox.value()))
                    self.plot_wave_vs_eff(sigmaeq, sigmalist, ranges, self.detector.blades, result, self.detector.wavelength)
                self.tabWidget_2.setCurrentIndex(0)
                self.optimizeThicknessSameButton.setEnabled(True)
                self.optimizeThicknessDiffButton.setEnabled(True)
                self.exportThickvseffButton.setEnabled(True)
                self.exportEffVsWaveButton.setEnabled(True)
                self.exportButton.setEnabled(True)
                self.optimizeThicknessDiffButton.setEnabled(True)
            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText("Please add wavelength")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                retval = msg.exec_()
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Please add blades")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            retval = msg.exec_()
        print ('')

    def plot_thick_vs_eff(self, sigma, ranges, blades, result):
        self.thickVsEffFigure.clear()
        #TODO change to plot_thick_vs_eff2
        self.detector.plot_thick_vs_eff(sigma, ranges, blades, result, self.thickVsEffFigure)
        self.thickVsEffCanvas.draw()

    def plot_wave_vs_eff(self,sigmaeq, sigmalist, ranges, blades, result, wavelength):
        self.waveVsEffFigure.clear()
        print('Monochromatic PLOT')
        # TODO change to plot_eff_vs_wave
        self.detector.plot_wave_vs_eff(sigmaeq, sigmalist, ranges, blades, result, wavelength,self.waveVsEffFigure)
        self.waveVsEffCanvas.draw()

    def plot_blade_figure(self, result):
        self.state = 'PlotBFigure'
        self.bladeEffFigure.clear()
        self.detector.plot_blade_figure(result, self.bladeEffFigure)
        for n in range(0, len(result[0])):
            item = QtWidgets.QTableWidgetItem(str(result[0][n][0] * 100)[:4] + '%')
            item.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.BladeTableWidget.setItem(n, 3, QtWidgets.QTableWidgetItem(item))
        self.bladeEffCanvas.draw()
        self.state = ''
        print ('plot blade figure multi blade')

    def plot_blade_figure_single(self, result):
        self.state = 'PlotBladeFigureSingle'
        self.bladeEffFigure.clear()
        self.detector.plot_blade_figure_single(result, self.bladeEffFigure)
        self.BladeTableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(str(result[0][0] * 100)[:4]+'% Backscattering, '+str(result[1][0] * 100)[:4]+'% Transmission'))
        self.bladeEffCanvas.draw()
        self.state = ''
        print ('Plot blade figure single coated blade')

    def optimize_thickness_same(self):
        self.detector.optimize_thickness_same()
        self.refresh_blades()
        self.calculate_total_efficiency()
        print ('Blade optimization with same thicknesses')

    def optimize_thickness_diff(self):
        if len(self.detector.wavelength) >= 1:
            self.detector.optimize_thickness_diff()
            self.refresh_blades()
            self.calculate_total_efficiency()
            print ('Blade optimization with different thicknesses')
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("This optimization needs wavelength set up")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            retval = msg.exec_()


    def export_plot_file(self, plot):
        """writes a two column file with x and y values of selected plots

        Args:
        	plot (String): key for metadata dict of desired plot

        """
        try:
            random = str(randint(0,100))
            filepath = str(QtWidgets.QFileDialog.getSaveFileName(self, "Select Directory"))
            if plot == 'effvsthick':
                meta = self.detector.metadata.get('thickVsEff')
                datafile_id = open(filepath, 'w+')
            if plot == 'effVsWave':
                datafile_id = open(filepath, 'w+')
                meta = self.detector.metadata.get('effVsWave')
            if plot == 'effvsdepth':
                datafile_id = open(filepath, 'w+')
                meta = self.detector.metadata.get('effvsdepth')
            if plot == 'thickDepth':
                datafile_id = open(filepath, 'w+')
                c = 0
                meta = [[],[]]
                for b in self.detector.blades:
                    meta[0].append(c+1)
                    meta[1].append(b.backscatter)
                    c += 1
            data = np.array([meta[0], meta[1]])
            for a, am in zip(data[0], data[1]):
                datafile_id.write("{}\t{}\n".format(a, am))
            datafile_id.close()
            print ('export plot file')
        except IOError:
            print ("Path error")

    def tableEdited(self, item):
        """signal triggered every time the blade table is updated, used to check the manual input from user to set up a specific thickness in a blade.
            checks that the input is a number and maximum of 8. Shows a message when the input is wrong.

        Args:
        	item: edited item

        """
        if self.state == '':
            try:
                itemText = float(item.text())
                if itemText > 8:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Warning)
                    msg.setText("Maximum thickness is 8")
                    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    retval = msg.exec_()
                    self.refresh_blades()
                else:
                    self.detector.blades[item.row()].backscatter = itemText
                    self.refresh_blades()
            except ValueError:
                self.refresh_blades()
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText("Wrong input")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                retval = msg.exec_()

    def export(self):
        self.detector.angle = self.angleSpinBox.value()
        self.detector.threshold = self.thresholdSpinBox.value()
        self.detector.converterConfiguration = str(self.converterComboBox.currentText())
        try:
            filepath = str(QtWidgets.QFileDialog.getSaveFileName(self, "Select Directory"))
            with open(str(filepath)+'.json', "w") as outfile:
                outfile.write(json.dumps(self.detector.to_json(), sort_keys=True, indent=4, ensure_ascii=False))
                outfile.close()
            print('Export JSON')
        except IOError:
            print ("Path error")

    def importWave(self):
        try:
            print ("Import wavelength")
            filepath = str(QtWidgets.QFileDialog.getOpenFileName(self, "Select Directory"))
            wave = np.loadtxt(filepath)
            weight = np.sum(np.loadtxt(filepath), axis=0)[1]
            try:
                if np.isclose(weight, 1):
                    self.waveTabWidget.show()
                    self.waveFormWidget.hide()
                    ax = self.waveInfoFigure.add_subplot(111)
                    ax.set_xlabel('Wavelength (angstrom)')
                    ax.set_ylabel('weight')
                    #ax.set_xlim([0, len(wave)])
                   # a = [[1, 2], [3, 3], [4, 4], [5, 2]]
                   # ax.plot(a, 'ro')
                    #ax.plot(wave)
                    x = wave[:,0]
                    y = wave[:, 1]
                    ax.plot(x,y*100,color='b')
                    ax.grid()
                    for w in wave:
                        self.detector.wavelength.append([w[0], w[1]*100])
                        rowPosition = self.lambdaTableWidget.rowCount()
                        self.lambdaTableWidget.insertRow(rowPosition)
                        self.lambdaTableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(w[0])))
                        self.lambdaTableWidget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(w[1]*100)))
                    self.deleteWaveButton.setEnabled(True)
                    print (str(self.detector.calculate_barycenter())+'= baricenter')
                    bari = self.detector.calculate_barycenter()
                    ax.plot([bari,bari],[0,ax.get_ylim()[1]], color='r')
                else:
                    raise Exception('Total Weight has to be 1, it is: '+ str(weight))
            except Exception as e:
                print('caught this error: ' + repr(e))
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText('Total Weight has to be 1, it is: ' + str(weight))
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                retval = msg.exec_()
        except IOError:
            print ("Path error")
