#!/usr/bin/env python

#from pylab import *
#from scipy import *
import pylab as pl
#import scipy as sp
import matplotlib.pyplot as plt
import numpy as np
import efftools
import Detector
import Blade
import B10


def calculate_eff_multiblade(nb,converterThickness, substrateThickness, wavelength, angle, threshold, single):
    assert nb >= 1
    assert len(wavelength) >= 1
    detector = Detector.Detector.build_multigrid_detector(nb, converterThickness, substrateThickness, wavelength, angle, threshold)
    return detector.calculate_eff()

if __name__ == '__main__':
    print calculate_eff_multiblade(10,1,0,[[1.8,100]], 90, 100,False)