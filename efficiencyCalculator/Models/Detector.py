import os
import sys
import math
import numpy as np
from bisect import bisect_left
import matplotlib.pyplot as plt
from scipy import interpolate
import B10
import efftools
import Blade
import copy
import json

class Detector:

    def __init__(self, name='Detector', angle=90, threshold=100, single=False):
        self.converter = B10.B10()
        self.name = name
        self.wavelength = []
        self.angle = angle
        self.threshold = threshold
        self.single = single
        self.metadata = {}
        self.blades = []

    def add_blade(self, blade):
        self.blades.append(blade)

    def add_blades(self, nb, thick):
        for i in nb:
            self.blades.append

    def add_wavelength(self, wavelength):
        self.wavelength.append(wavelength)

    def calculate_eff(self):
        assert len(self.blades) >= 1
        assert len(self.wavelength) >= 1
        ranges = self.calculate_ranges()
        sigma = self.calculate_sigma()
        if self.single:
            print 'Boron single layer calculation '
            result = efftools.efficiency2particles(self.blades[0].backscatter, ranges[0], ranges[1], sigma)
        else:
            print 'Boron multi-blade double coated calculation '
            result = efftools.data_samethick_vs_thickandnb_depth(sigma, ranges, self.blades)
        return result

    def calculate_ranges(self):
        """calculates range of 4 particles given a threshold and configuration of B10.

        Returns:
        	    r[1,4]: r(1,1)=ralpha_94;
                 r(1,2)=rLi_94;
                 r(1,3)=ralpha_06;
                 r(1,4)=rLi_06;

            ranges in um

        ..  Original source in Matlab: https://bitbucket.org/europeanspallationsource/dg_matlabborontools/src/bcbac538ad10d074c5150a228847efc2e0269e0d/B10tools/rangesMAT.m?at=default&fileviewer=file-view-default

        """
        return self.converter.ranges(self.threshold, '10B4C 2.24g/cm3')

    def calculate_sigma(self):
        """calculates sigma equivalent of Boron depending on sigma and angle
               ..  Original source in Matlab: https://bitbucket.org/europeanspallationsource/dg_matlabborontools/src/bcbac538ad10d074c5150a228847efc2e0269e0d/B10tools/macroB10sigma.m?at=default&fileviewer=file-view-default

               """
        return self.converter.full_sigma_calculation(self.wavelength, self.angle)

    def plot_blade_figure(self, eff, figure):
        """plots the efficiency of all blades,

        Returns:
        	plotted figure

            reference: figure 3.14 On Francesco's Thesis
        """
        if eff is None:
            eff = self.calculate_eff()
        ax = figure.add_subplot(111)
        ax.set_xlabel('Blade Number')
        ax.set_ylabel('Blade efficiency (%)')
        ax.set_ylim([0, (eff[1] * 100 + 1)])
        ax.set_xlim([0, len(eff[0]) + 1])
        ax.plot(0, 0)
        ax.plot(0, len(eff[0]) + 1)
        # ax.plot(nb + 1, 0)
        for n in range(0, len(eff[0])):
            # Note that the plot displayed is the backscattering thickness
            ax.plot(n + 1, eff[0][n][1] * 100, 'o', color='red')
        ax.grid(True)
        return ax

    def plot_blade_figure_single(self, result, figure):
        """plots the efficiency of a single layer,

        Returns:
        	plotted figure\
        """
        ax = figure.add_subplot(111)
        ax.set_xlabel('Blade Number')
        ax.set_ylabel('Blade efficiency (%)')
        ax.set_ylim([0, (result[1] * 100 + 1)])
        ax.set_xlim([0, len(result[0]) + 1])
        ax.plot(0, 0)
        ax.plot(0, len(result[0]) + 1)
        # ax.plot(nb + 1, 0)
        ax.plot(1, result[0][0] * 100, 'o', label=" BS", color='red')
        ax.plot(1, result[1][0] * 100, 'o', label=" TS", color='b')
        ax.legend(numpoints=1)
        ax.grid(True)
        return ax

    #TODO change plot functions so they don't need arguments. Make a script function with the arguments that calls this
    def plot_thick_vs_eff(self, sigma, ranges, blades, result, figure):
        """plots the efficiency function for a set of thicknesses,

        Args:
            sigma: Full sigma calculation fo the detector
            ranges: Ranges calculation
            blades: detector blades
            result: Efficiency
            figure: figure to plot in

        Returns:
        	plotted figure
            reference: figure 3.12 On Francesco's Thesis
        """
        bx = figure.add_subplot(111)
        if self.single:
            thickVsEff = efftools.metadata_samethick_vs_thickandnb_single(sigma, ranges, len(blades))
            bx.plot(thickVsEff[0], thickVsEff[1])
            bx.grid(True)
            bx.set_xlabel('Blade thickness')
            bx.set_ylabel('Detector efficiency (%)')
            line = bx.plot([self.blades[0].backscatter, self.blades[0].backscatter],
                           [0, result[1][0] * 100], '--')
            plt.setp(line, 'color', 'k', 'linewidth', 0.5)
        else:
            thickVsEff = efftools.metadata_samethick_vs_thickandnb(sigma, ranges, len(blades))
            self.metadata.update({'thickVsEff': thickVsEff})
            bx.plot(thickVsEff[0], thickVsEff[1])
            bx.grid(True)
            bx.set_xlabel('Blade thickness')
            bx.set_ylabel('Detector efficiency (%)')
            line = bx.plot([self.blades[0].backscatter, self.blades[0].backscatter], [0, result[1]],
                           '--')
            plt.setp(line, 'color', 'k', 'linewidth', 0.5)
        if self.single:
            line2 = bx.plot([0, self.blades[0].backscatter], [result[1][0], result[1][0]], '--')
        else:
            line2 = bx.plot([0, self.blades[0].backscatter], [result[1], result[1]], '--')
        plt.setp(line2, 'color', 'k', 'linewidth', 0.5)
      #  ticks = bx.get_yticks() * 100
       # bx.set_yticklabels(ticks)
        return bx

    def plot_thick_vs_eff2(self):
        """plots the efficiency function for a set of thicknesses,

        Args:
            sigma: Full sigma calculation fo the detector
            ranges: Ranges calculation
            blades: detector blades
            result: Efficiency
            figure: figure to plot in

        Returns:
        	plotted figure
            reference: figure 3.12 On Francesco's Thesis
        """
        sigma = self.calculate_sigma()
        ranges = self.calculate_ranges()
        blades = self.blades
        result = self.calculate_eff()
        bx = plt.figure(1)
        plt.subplot(111)
        if self.single:
            thickVsEff = efftools.metadata_samethick_vs_thickandnb_single(sigma, ranges, len(blades))
            plt.plot(thickVsEff[0], thickVsEff[1])
            plt.grid(True)
            plt.xlabel('Blade thickness')
            plt.ylabel('Detector efficiency (%)')
            line = plt.plot([self.blades[0].backscatter, self.blades[0].backscatter],
                           [0, result[1][0] * 100], '--')
            plt.setp(line, 'color', 'k', 'linewidth', 0.5)
        else:
            thickVsEff = efftools.metadata_samethick_vs_thickandnb(sigma, ranges, len(blades))
            self.metadata.update({'thickVsEff': thickVsEff})
            plt.plot(thickVsEff[0], thickVsEff[1])
            plt.grid(True)
            plt.xlabel('Blade thickness')
            plt.ylabel('Detector efficiency (%)')
            line = plt.plot([self.blades[0].backscatter, self.blades[0].backscatter], [0, result[1]],
                           '--')
            plt.setp(line, 'color', 'k', 'linewidth', 0.5)
        if self.single:
            line2 = plt.plot([0, self.blades[0].backscatter], [result[1][0], result[1][0]], '--')
        else:
            line2 = plt.plot([0, self.blades[0].backscatter], [result[1], result[1]], '--')
        plt.setp(line2, 'color', 'k', 'linewidth', 0.5)
      #  ticks = bx.get_yticks() * 100
       # bx.set_yticklabels(ticks)
        return bx

    def plot_wave_vs_eff(self,sigmaeq, sigmalist, ranges, blades, result, wavelength, figure):
        """plots the efficiency for a set of wavelengths,

        Args:
            sigma: Full sigma calculation fo the detector
            ranges: Ranges calculation
            blades: detector blades
            result: Efficiency
            figure: figure to plot in

        Returns:
        	plotted figure
            reference: figure 3.13 On Francesco's Thesis
        """
        if sigmaeq == None:
            sigmaeq = self.calculate_sigma()
        if ranges == None:
            sigmaeq = self.calculate_ranges()
        if self.single:
            y = efftools.metadata_singleLayer_vs_wave(sigmaeq, blades[0].backscatter, ranges, len(blades))
        else:
            y = efftools.metadata_diffthick_vs_wave(sigmaeq, blades, ranges, len(blades))
        cx = figure.add_subplot(111)
        self.metadata.update({'effVsWave': [sigmalist, y]})
        cx.plot(sigmalist, y, color='g')
        if self.single:
            cx.plot([wavelength[0][0], wavelength[0][0]], [0, result[1][0]], '--',
                    color='k')
            cx.plot([0, wavelength[0][0]], [result[1][0], result[1][0]], '--', color='k')
        else:
            cx.plot([wavelength[0][0], wavelength[0][0]], [0, result[1]], '--',
                    color='k')
            cx.plot([0, wavelength[0][0]], [result[1], result[1]], '--', color='k')
        cx.grid(True)
        cx.set_xlabel('Neutron wavelength (Angstrom)')
        cx.set_ylabel('Detector efficiency (%)')
      #  ticks = cx.get_yticks() * 100
       # cx.set_yticklabels(ticks)
        return cx

    def plot_eff_vs_wave(self):
        """plots the efficiency for a set of wavelengths,

        Args:
            sigma: Full sigma calculation fo the detector
            ranges: Ranges calculation
            blades: detector blades
            result: Efficiency
            figure: figure to plot in

        Returns:
        	plotted figure
            reference: figure 3.13 On Francesco's Thesis
        """
        sigmalist = np.arange(0.0011, 20, 0.1)
        sigmaeq = []
        for sigma in sigmalist:
            # transformation for meeting requirements of functions
            sigma = [[sigma], ]
            sigmaeq.append(B10.B10().full_sigma_calculation(sigma, self.angle))
        ranges = self.calculate_ranges()
        blades = self.blades
        result = self.calculate_eff()
        wavelength = self.wavelength
        y = efftools.metadata_samethick_vs_wave(sigmaeq, blades[0].backscatter, ranges, len(blades))
        cx = plt.figure(1)
        plt.subplot(111)
        self.metadata.update({'effVsWave': [sigmalist, y]})
        plt.plot(sigmalist, y, color='g')
        if self.single:
            plt.plot([wavelength[0][0], wavelength[0][0]], [0, result[1][0]], '--',
                    color='k')
            plt.plot([0, wavelength[0][0]], [result[1][0], result[1][0]], '--', color='k')
        else:
            plt.plot([wavelength[0][0], wavelength[0][0]], [0, result[1]], '--',
                    color='k')
            plt.plot([0, wavelength[0][0]], [result[1], result[1]], '--', color='k')
        plt.grid(True)
        plt.xlabel('Neutron wavelength (Angstrom)')
        plt.ylabel('Detector efficiency (%)')
      #  ticks = cx.get_yticks() * 100
       # cx.set_yticklabels(ticks)
        return cx

    def optimize_thickness_same(self):
        """sets the thickness of all blades to the most optimal,

        Args:
            sigma: Full sigma calculation fo the detector
            ranges: Ranges calculation
            blades: detector blades
            result: Efficiency
            figure: figure to plot in

        Returns:
        	plotted figure
            reference: figure 3.13 On Francesco's Thesis
        """
        #meta = self.metadata.get('thickVsEff')
        meta = efftools.metadata_samethick_vs_thickandnb(self.calculate_sigma(), self.calculate_ranges(), len(self.blades))
        max = np.array(meta[1]).argmax()
        c = 0
        max = meta[0][max]
        nb = len(self.blades)
        for b in self.blades:
            b.backscatter = max
            self.blades[c] = b
            c += 1

    @staticmethod
    def build_multigrid_detector(nb, converterThickness, substrateThickness, wavelength, angle, threshold):
        bladelist = []
        blade = Blade.Blade(converterThickness,converterThickness,substrateThickness,0)
        for x in range(0,nb):
            bladelist.append(copy.deepcopy(blade))
        detector = Detector()
        detector.blades = bladelist
        detector.wavelength = wavelength
        detector.angle = angle
        detector.threshold = threshold
        return detector

    @staticmethod
    def json_parser(path):
        try:
            with open(path) as data_file:
                data = json.load(data_file)
            wave =[]
            for w in data.get('wavelength'):
                wave.append([w.get('angstrom'), w.get('%')])
            detector = Detector.build_multigrid_detector(len(data.get('blades')),data.get('blades')[0].get('backscatter'),data.get('blades')[0].get('substrate'),wave, data.get('angle'), data.get('threshold'))
            # Access data
            return detector
        except (ValueError, KeyError, TypeError):
            print "JSON format error"

    def to_json(self):
        d = {}
        d["name"] = self.name
        d["converter"] = '10B4C 2.24g/cm3'
        d["angle"] = self.angle
        d["threshold"] = self.threshold
        blades = []
        for b in self.blades:
            bdict = {}
            bdict["backscatter"] = b.backscatter
            bdict["transmission"] = b.transmission
            bdict["substrate"] = b.substrate
            bdict["inclination"] = b.inclination
            blades.append(bdict)
        wavelength = []
        for w in self.wavelength:
            wdict = {}
            wdict["%"] = w[1]
            wdict["angstrom"] = w[0]
            wavelength.append(wdict)
        d["blades"] = blades
        d["single"] = self.single
        d["wavelength"] = wavelength
        return d


if __name__ == '__main__':
   #Detector.json_parser('/Users/alvarocbasanez/PycharmProjects/dg_efficiencycalculator/efficiencyCalculator/exports/detector1.json')
   detector = Detector.build_multigrid_detector(10,1,0,[[1.8,100]], 90, 100)
   detector.to_json()