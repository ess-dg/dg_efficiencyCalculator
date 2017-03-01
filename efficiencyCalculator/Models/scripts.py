#!/usr/bin/env python

import json
import Detector
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

def calculate_eff_multiblade(nb,converterThickness, substrateThickness, wavelength, angle, threshold, single):
    assert nb >= 1
    assert len(wavelength) >= 1
    detector = Detector.Detector.build_multigrid_detector(nb, converterThickness, substrateThickness, wavelength, angle, threshold)
    return detector.calculate_eff()

def calculate_eff_json(path):
    print 'Script eff json'
    detector = Detector.Detector.json_parser(path)
    return detector.calculate_eff()

def plot_eff_vs_thick(path):
    detector = Detector.Detector.json_parser(path)
    detector.plot_thick_vs_eff2()
    plt.show()

def plot_eff_vs_wave(path):
    detector = Detector.Detector.json_parser(path)
    detector.plot_eff_vs_wave()
    plt.show()

def optimize_config(originPath, destinyPath):
    detector = Detector.Detector.json_parser(originPath)
    detector.optimize_thickness_same()
    detector.to_json()
    try:
        filepath = destinyPath
        with open(str(filepath) + '/' + detector.name + '_optimized_config.json', "w") as outfile:
            outfile.write(json.dumps(detector.to_json(), sort_keys=True, indent=4, ensure_ascii=False))
            outfile.close()
        print('Export')
    except IOError:
        print "Path error"




if __name__ == '__main__':
    print calculate_eff_multiblade(10,1,0,[[1.8,100]], 90, 100,False)
    print calculate_eff_json('/Users/alvarocbasanez/PycharmProjects/dg_efficiencycalculator/efficiencyCalculator/exports/detector1.json')
    plot_eff_vs_thick('/Users/alvarocbasanez/PycharmProjects/dg_efficiencycalculator/efficiencyCalculator/exports/detector1.json')
    optimize_config('/Users/alvarocbasanez/PycharmProjects/dg_efficiencycalculator/efficiencyCalculator/exports/detector1.json', '/Users/alvarocbasanez/PycharmProjects/dg_efficiencycalculator/efficiencyCalculator/exports')
    plot_eff_vs_wave('/Users/alvarocbasanez/PycharmProjects/dg_efficiencycalculator/efficiencyCalculator/exports/detector1.json')
