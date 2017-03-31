import matplotlib
import matplotlib.figure
import json
import  sys
import matplotlib.pyplot as plt
import numpy as np
from PyQt4 import QtGui, QtCore, uic, Qt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from random import randint

import Models.B10 as B10
import Models.Blade as Blade
from Models import efftools


class detectorDialog( QtGui.QDialog):

    def __init__(self, detector, action, parent = None):
        super(detectorDialog, self).__init__(parent)
        uic.loadUi("detectorDialogTab.ui", self)

        self.state = ''
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
        self.thickVsEff = []
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
        self.toolbar = NavigationToolbar(self.thickVsEffCanvas, self)
        self.toolbar2 = NavigationToolbar(self.waveVsEffCanvas, self)
        self.thickToolLayout.addWidget(self.toolbar)
        self.waveToolLayout.addWidget(self.toolbar2)
        # self.toolbar.hide()
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

                    item = QtGui.QTableWidgetItem('Blade N:'+str(c+1))
                    # execute the line below to every item you need locked
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

                    self.BladeTableWidget.setItem(rowPosition, 0, QtGui.QTableWidgetItem(item))

                    item = QtGui.QTableWidgetItem(str(b.backscatter))
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                    self.BladeTableWidget.setItem(rowPosition, 1, item)

                  #  self.BladeTableWidget.setItem(rowPosition, 2, QtGui.QTableWidgetItem(str(b.transmission)))

                    item = QtGui.QTableWidgetItem(str(b.substrate))
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                    self.BladeTableWidget.setItem(rowPosition, 2, QtGui.QTableWidgetItem(item))

                    item = QtGui.QTableWidgetItem('unknown')
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.BladeTableWidget.setItem(rowPosition, 3, QtGui.QTableWidgetItem(item))
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
        self.addPoliWavelengthButton.clicked.connect(lambda: self.add_poli_wavelength())
        self.deleteBladeButton.clicked.connect(lambda: self.delete_blades())
        self.deleteButton.clicked.connect(lambda: self.delete_detector())
        self.calculateTotalEffButton.clicked.connect(lambda: self.calculate_total_efficiency())
        self.optimizeThicknessSameButton.clicked.connect(lambda: self.optimize_thickness_same())
        self.optimizeThicknessDiffButton.clicked.connect(lambda: self.optimize_thickness_diff())
        self.exportButton.clicked.connect(lambda: self.export())
        self.exportThickvseffButton.clicked.connect(lambda: self.export_plot_file('effvsthick'))
        self.exportEffVsWaveButton.clicked.connect(lambda: self.export_plot_file('effVsWave'))
        self.nameLineEdit.textChanged.connect(lambda: self.updateDetector())

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
        self.detector.name = str(self.nameLineEdit.text())
        self.detector.threshold = self.thresholdSpinBox.value()
        self.detector.angle = self.angleSpinBox.value()

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

    def add_poli_wavelength(self):
        self.detector.wavelength.append([self.wavePoliSpinBox.value(), self.percentPoliSpinBox.value()])
        rowPosition = self.lambdaTableWidget.rowCount()
        self.lambdaTableWidget.insertRow(rowPosition)
        self.lambdaTableWidget.setItem(rowPosition, 0, QtGui.QTableWidgetItem(str(self.wavePoliSpinBox.value())))
        self.lambdaTableWidget.setItem(rowPosition, 1, QtGui.QTableWidgetItem(str(self.percentPoliSpinBox.value())))
        self.percentPoliSpinBox.setMaximum(self.percentPoliSpinBox.maximum() - self.percentPoliSpinBox.value())
        # self.addPoliWavelengthButton.setEnabled(False)
        self.deleteWaveButton.setEnabled(True)
        if self.percentPoliSpinBox.maximum() == 0:
            self.addPoliWavelengthButton.setEnabled(False)

    def delete_wavelength(self):
        self.detector.wavelength = []
        self.lambdaTableWidget.setRowCount(0)
        self.addWavelengthButton.setEnabled(True)
        self.addPoliWavelengthButton.setEnabled(True)
        self.deleteWaveButton.setEnabled(False)
        self.bladeEffFigure.clear()
        self.bladeEffCanvas.draw()
        self.totalEfflabel.setText('unknown')
        self.percentPoliSpinBox.setMaximum(100)
        self.percentPoliSpinBox.setValue(100)

    def refresh_blades(self):
        self.state = 'RefressB'
        self.bladeInfoFigure.clear()
        ax = self.bladeInfoFigure.add_subplot(111)
        ax.set_xlabel('Blade Number')
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
            self.BladeTableWidget.setItem(n, 0, QtGui.QTableWidgetItem(str(n + 1)))
            self.BladeTableWidget.setItem(n, 1, QtGui.QTableWidgetItem(str(bs)))
            self.BladeTableWidget.setItem(n, 2, QtGui.QTableWidgetItem(str(sub)))
        ax.grid(True)
        self.bladeInfoCanvas.draw()
        self.state = ''

    def add_blades(self):
        if self.bsSpinBox.value() > 0:
            self.state = 'AddB'
            self.tabWidget_2.setCurrentIndex(0)
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
                item = QtGui.QTableWidgetItem(str(bs))
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                self.BladeTableWidget.setItem(n, 1, item)
                self.BladeTableWidget.setItem(n, 2, QtGui.QTableWidgetItem(str(sub)))
            ax.grid(True)
            self.bladeInfoCanvas.draw()
            self.addBladeButton.setEnabled(False)
            self.addSingleBladeButton.setEnabled(False)
            self.deleteBladeButton.setEnabled(True)
            self.detector.single = False
            self.state = ''
        else:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Warning)
            msg.setText("Please set thickness")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            retval = msg.exec_()

    def add_layer(self):
        self.state = 'addLayer'
        bs =0
        ts=0
        self.tabWidget_2.setCurrentIndex(0)
        if self.bsSingleSpinBox.value() > 0:

            ax = self.bladeInfoFigure.add_subplot(111)
            ax.set_xlabel('Blade Number')
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
        self.state = ''

    def delete_blades(self):
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
        print 'CalculateTotalEff'
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
                        '<html><head/><body><p><span style=" font-size:24pt; font-weight:600;"> BS: ' + str(result[0][0] * 100)[:4] + '% Ts: ' + str(result[1][0] * 100)[:4])
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
                self.tabWidget_2.setCurrentIndex(2)
                self.optimizeThicknessSameButton.setEnabled(True)
                self.optimizeThicknessDiffButton.setEnabled(True)
                self.exportThickvseffButton.setEnabled(True)
                self.exportEffVsWaveButton.setEnabled(True)
                self.exportButton.setEnabled(True)
                self.optimizeThicknessDiffButton.setEnabled(True)
            else:
                msg = QtGui.QMessageBox()
                msg.setIcon(QtGui.QMessageBox.Warning)
                msg.setText("Please add wavelength")
                msg.setStandardButtons(QtGui.QMessageBox.Ok)
                retval = msg.exec_()
        else:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Warning)
            msg.setText("Please add blades")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            retval = msg.exec_()
        print ''

    def plot_thick_vs_eff(self, sigma, ranges, blades, result):
        self.thickVsEffFigure.clear()
        #TODO change to plot_thick_vs_eff2
        self.detector.plot_thick_vs_eff(sigma, ranges, blades, result, self.thickVsEffFigure)
        self.thickVsEffCanvas.draw()

    def plot_wave_vs_eff(self,sigmaeq, sigmalist, ranges, blades, result, wavelength):
        self.waveVsEffFigure.clear()
        print('   Monochromatic PLOT')
        # TODO change to plot_eff_vs_wave
        self.detector.plot_wave_vs_eff(sigmaeq, sigmalist, ranges, blades, result, wavelength,self.waveVsEffFigure)
        self.waveVsEffCanvas.draw()


    def plot_blade_figure(self, result):
        self.state = 'PlotBFigure'
        self.bladeEffFigure.clear()
        self.detector.plot_blade_figure(result, self.bladeEffFigure)
        for n in range(0, len(result[0])):
            item = QtGui.QTableWidgetItem(str(result[0][n][0] * 100)[:4] + '%')
            item.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.BladeTableWidget.setItem(n, 3, QtGui.QTableWidgetItem(item))
        self.bladeEffCanvas.draw()
        self.state = ''

    def plot_blade_figure_single(self, result):
        self.state = 'PlotBladeFigureSingle'
        self.bladeEffFigure.clear()
        self.detector.plot_blade_figure_single(result, self.bladeEffFigure)
        self.BladeTableWidget.setItem(0, 3, QtGui.QTableWidgetItem(str(result[0][0] * 100)[:4]+'% BS, '+str(result[1][0] * 100)[:4]+'% TS'))
        self.bladeEffCanvas.draw()
        self.state = ''

    def optimize_thickness_same(self):
        self.detector.optimize_thickness_same()
        self.refresh_blades()
        self.calculate_total_efficiency()

    def optimize_thickness_diff(self):
        if len(self.detector.wavelength) == 1:
            self.detector.optimize_thickness_diff_mono()
            self.refresh_blades()
            self.calculate_total_efficiency()
        else:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Warning)
            msg.setText("This optimization is only available with monochromatic neutron beam")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            retval = msg.exec_()


    def export_plot_file(self, plot):
        """writes a two column file with x and y values of selected plots

        Args:
        	plot (String): key for metadata dict of desired plot

        """
        try:
            random = str(randint(0,100))
            filepath = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
            if plot == 'effvsthick':
                meta = self.detector.metadata.get('thickVsEff')
                datafile_id = open(filepath + '/'+self.detector.name+random+'thickVsEff.txt', 'w+')
            if plot == 'effVsWave':
                datafile_id = open(filepath + '/'+self.detector.name+random+'effVsWave.txt', 'w+')
                meta = self.detector.metadata.get('effVsWave')
            data = np.array([meta[0], meta[1]])
            for a, am in zip(data[0], data[1]):
                datafile_id.write("{}\t{}\n".format(a, am))
            datafile_id.close()
        except IOError:
            print "Path error"

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
                    msg = QtGui.QMessageBox()
                    msg.setIcon(QtGui.QMessageBox.Warning)
                    msg.setText("Maximum thickness is 8")
                    msg.setStandardButtons(QtGui.QMessageBox.Ok)
                    retval = msg.exec_()
                    self.refresh_blades()
                else:
                    self.detector.blades[item.row()].backscatter = itemText
                    self.refresh_blades()
            except ValueError:
                self.refresh_blades()
                msg = QtGui.QMessageBox()
                msg.setIcon(QtGui.QMessageBox.Warning)
                msg.setText("Wrong input")
                msg.setStandardButtons(QtGui.QMessageBox.Ok)
                retval = msg.exec_()

    def export(self):
        try:
            filepath = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
            with open(str(filepath)+'/'+self.detector.name+'config.json', "w") as outfile:
                outfile.write(json.dumps(self.detector.to_json(), sort_keys=True, indent=4, ensure_ascii=False))
                outfile.close()
            print('Export')
        except IOError:
            print "Path error"
