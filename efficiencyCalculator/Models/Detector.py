import os
import sys
import math
import numpy as np
from bisect import bisect_left
import matplotlib.pyplot as plt
from scipy import interpolate

class Detector:
    name = ''
    blades = []
    wavelength = []
    angle = 0
    threshold = 0

    def __init__(self, name):
        self.name = name

    def add_blade(self,blade):
        self.blades.append(blade)

    def add_wavelength(self, wavelength):
        self.wavelength.append(wavelength)


    def optimize_thickness_different(self):
        a=-1

    def optimize_thickness_same(self):
        a=0

    def plot_eff_vs_thick(self):
        a = 1

    def plot_eff_vs_wavelength(self):
        a=2

    def plot_blade_eff(self):
        a=3

    def plot_blade_thick(self):
        a=4

class Blade:
    backscatter = 0.0
    transmission = 0.0
