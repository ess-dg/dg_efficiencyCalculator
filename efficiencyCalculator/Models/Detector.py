import os
import sys
import math
import numpy as np
from bisect import bisect_left
import matplotlib.pyplot as plt
from scipy import interpolate
import B10
import efftools

class Detector:

    def __init__(self, name):
        self.converter = B10.B10()
        self.name = name
        self.blades = []
        self.wavelength = []
        self.angle = 90
        self.threshold = 100
        self.single = False
        self.metadata = []

    def add_blade(self,blade):
        self.blades.append(blade)

    def add_wavelength(self, wavelength):
        self.wavelength.append(wavelength)

    def calculate_eff(self):
        assert len(self.blades) >= 1
        assert len(self.wavelength) >= 1
        eff = 1
        ranges = self.converter.ranges(self.threshold, '10B4C 2.24g/cm3')
        sigma = self.converter.full_sigma_calculation(self.wavelength, self.angle)
        if self.single:
            print 'Boron single layer calculation '
            result = efftools.efficiency2particles(self.blades[0].backscatter, ranges[0], ranges[1], sigma)
        else:
            print 'Boron multi-blade double coated calculation '
            result = efftools.data_samethick_vs_thickandnb_depth(sigma, ranges, self.blades)
        return result

class Blade:
    backscatter = 0.0
    transmission = 0.0
