#!/usr/bin/env python
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

base, form = uic.loadUiType("efficiencyMainwindow.ui")


class Window(base, form):
    converters = {}

    def __init__(self,  parent=None):
        super(base, self).__init__(parent)
        # init list of converter materials, load data and add to converter dict
        self.converter_list()
        self.start_window()
        sys.exit(app.exec_())

    def converter_list(self):
        boron10 = B10.B10()
        self.converters.update(B10=boron10)

    def start_window(self):
        self.setupUi(self)
        # Read from converter dict and place a selector in converterComboBox
        for c in self.converters:
            configs = self.converters.get(c).configurations
            for conf in configs:
                self.converterComboBox.addItem(conf.get('name'))
        # connect calculation functionality to the button
        self.calculatePushButton.clicked.connect(lambda: self.calculate_efficiency())
        # Include figure to place the plot
       # self.figure = matplotlib.figure.Figure()
        #self.canvas = FigureCanvas(self.figure)
        #self.plotLayout.addWidget(self.canvas)
        self.show()

    def calculate_efficiency(self):
        self.figure.clf()
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
        self.plotstoppingpower()

    def plotstoppingpower(self):
        figure1 = matplotlib.figure.Figure()
        names = ["IONIZ_Linkoping_Alpha06.txt","IONIZ_Linkoping_Alpha94.txt","IONIZ_Linkoping_Li06.txt","IONIZ_Linkoping_Li94.txt"]
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
            print name + ': '
            print integral
            print

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
        plt.subplot(212)
        plt.xlabel('x (um)')
        plt.ylabel('Erem (KeV)')
        # threshold horizontal line
        plt.plot([0, 50000], [threshold, threshold], color='k', linestyle='--', linewidth=1, label='Threshold ')
        # plt.legend()
        self.canvas.draw_idle()



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    #initialize app's main controller
    #controller = MainController()
    Window()
