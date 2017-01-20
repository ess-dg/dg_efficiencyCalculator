import os
import sys
import math
import numpy as np
from bisect import bisect_left
import matplotlib.pyplot as plt
from scipy import interpolate

class Detector:

    def __init__(self, name):
        self.name = name
        self.blades = []
        self.wavelength = []
        self.angle = 90
        self.threshold = 100
        self.single = False

    def add_blade(self,blade):
        self.blades.append(blade)

    def add_wavelength(self, wavelength):
        self.wavelength.append(wavelength)


class Blade:
    backscatter = 0.0
    transmission = 0.0
