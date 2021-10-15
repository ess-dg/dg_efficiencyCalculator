#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from os.path import dirname, abspath, join
import sys

# Find code directory relative to our directory
THIS_DIR = dirname(__file__)
CODE_DIR = abspath(join(THIS_DIR, '../../..', 'dg_efficiencyCalculator'))
sys.path.append(CODE_DIR)

import neutron_detector_eff_functions.Aluminium as Aluminium
import neutron_detector_eff_functions.Converter as Converter
import neutron_detector_eff_functions.efftools as efftools
import neutron_detector_eff_functions.B10 as B10
import itertools
import shutil
import os
import analysis_helper_functions as hf

# ==============================================================================
#                                DEFINE PARAMETERS
# ==============================================================================

# General parameters
B10_object = B10.B10()
al_sub = 500 # um
inclination = 90
threshold = 120
ranges = B10_object.ranges(threshold, '10B4C 2.24g/cm3')
wavelengths = np.linspace(2, 20, 100)
coatings_ideal = np.concatenate((np.ones(7) * 0.5,
                                 np.ones(7) * 1,
                                 np.ones(3) * 1.5))

# Blade positions relative to triple blade center (cm)
center_blade_1 = -7.325
center_blade_2 = 7.325
top_blade_1 = 7.925
top_blade_2 = 22.575
bottom_blade_1 = -22.575
bottom_blade_2 = -7.925


# ==============================================================================
#                            GET THICKNESS DISTRIBUTION
# ==============================================================================

xx = np.linspace(-25, 25, 200)
yy = hf.get_triple_blade_thickness_distribution(xx)

xx_b = np.linspace(bottom_blade_1, bottom_blade_2, 100)
yy_b = hf.get_triple_blade_thickness_distribution(xx_b)
xx_c = np.linspace(center_blade_1, center_blade_2, 100)
yy_c = hf.get_triple_blade_thickness_distribution(xx_c)
xx_t = np.linspace(top_blade_1, top_blade_2, 100)
yy_t = hf.get_triple_blade_thickness_distribution(xx_t)

fig = plt.figure()
plt.plot(xx, yy, label='Thickness distribution', color='black')
plt.fill_between(xx_b, yy_b, color='blue', zorder=3,
                alpha=0.7, label='Bottom blade')
plt.fill_between(xx_c, yy_c, color='green', zorder=3,
                 alpha=0.7, label='Center blade')
plt.fill_between(xx_t, yy_t, color='red', zorder=3,
                  alpha=0.7, label='Top blade')
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Triple blade position (cm)')
plt.ylabel('Relative thickness')
plt.legend()
plt.xlim(-25, 25)
plt.ylim(0, 1)
plt.title('Thickness relative to center of triple blade')
plt.savefig('../output/trex_triple_blade_thickness_distribution.pdf')
plt.close()

# ==============================================================================
#                   INVESTIGATION OF SUGGESTED CONFIGURATIONS
# ==============================================================================

ideal_efficiency = hf.get_efficiency_vs_lambda(wavelengths, ranges, B10_object,
                                               al_sub, coatings_ideal, inclination)
# Define number of data points
number_data_points = 20
# Get points along the blades
center_blade_points = np.linspace(center_blade_1, center_blade_2, number_data_points)
top_blade_points = np.linspace(top_blade_1, top_blade_2, number_data_points)
bottom_blade_points = np.linspace(bottom_blade_1, bottom_blade_2, number_data_points)
# Get corresponding thicknesses along the blade
center_blade_relative = hf.get_triple_blade_thickness_distribution(center_blade_points)
top_blade_relative = hf.get_triple_blade_thickness_distribution(top_blade_points)
bottom_blade_relative = hf.get_triple_blade_thickness_distribution(bottom_blade_points)
# Declare aimed thicknesses (um)
section_A = 0.65
section_B = 1.15
# Declare coatings thicknesses
center_blade_A = section_A * center_blade_relative
top_blade_A = section_A * top_blade_relative
bottom_blade_A = section_A * bottom_blade_relative

center_blade_B = section_B * center_blade_relative
top_blade_B = section_B * top_blade_relative
bottom_blade_B = section_B * bottom_blade_relative
# Declare coating configuration alternatives
# coatings_TT = np.array([top_blade_A,    # Change blade here
#                         top_blade_A,
#                         bottom_blade_A,
#                         top_blade_A,
#                         bottom_blade_A,
#                         top_blade_A,    # Change blade here
#                         center_blade_A,
#                         center_blade_A,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         center_blade_B,
#                         center_blade_B,
#                         center_blade_B])
#
# coatings_CT = np.array([center_blade_A,    # Change blade here
#                         top_blade_A,
#                         bottom_blade_A,
#                         top_blade_A,
#                         bottom_blade_A,
#                         top_blade_A,    # Change blade here
#                         center_blade_A,
#                         center_blade_A,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         center_blade_B,
#                         center_blade_B,
#                         center_blade_B])
#
# coatings_BT = np.array([bottom_blade_A,    # Change blade here
#                         top_blade_A,
#                         bottom_blade_A,
#                         top_blade_A,
#                         bottom_blade_A,
#                         top_blade_A,    # Change blade here
#                         center_blade_A,
#                         center_blade_A,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         center_blade_B,
#                         center_blade_B,
#                         center_blade_B])
#
# coatings_TC = np.array([top_blade_A,    # Change blade here
#                         top_blade_A,
#                         bottom_blade_A,
#                         top_blade_A,
#                         bottom_blade_A,
#                         center_blade_A,    # Change blade here
#                         center_blade_A,
#                         center_blade_A,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         center_blade_B,
#                         center_blade_B,
#                         center_blade_B])
#
# coatings_CC = np.array([center_blade_A,    # Change blade here
#                         top_blade_A,
#                         bottom_blade_A,
#                         top_blade_A,
#                         bottom_blade_A,
#                         center_blade_A,    # Change blade here
#                         center_blade_A,
#                         center_blade_A,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         center_blade_B,
#                         center_blade_B,
#                         center_blade_B])
#
# coatings_BC = np.array([bottom_blade_A,    # Change blade here
#                         top_blade_A,
#                         bottom_blade_A,
#                         top_blade_A,
#                         bottom_blade_A,
#                         center_blade_A,    # Change blade here
#                         center_blade_A,
#                         center_blade_A,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         center_blade_B,
#                         center_blade_B,
#                         center_blade_B])
#
# coatings_TB = np.array([top_blade_A,    # Change blade here
#                         top_blade_A,
#                         bottom_blade_A,
#                         top_blade_A,
#                         bottom_blade_A,
#                         bottom_blade_A,    # Change blade here
#                         center_blade_A,
#                         center_blade_A,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         center_blade_B,
#                         center_blade_B,
#                         center_blade_B])
#
# coatings_CB = np.array([center_blade_A,    # Change blade here
#                         top_blade_A,
#                         bottom_blade_A,
#                         top_blade_A,
#                         bottom_blade_A,
#                         bottom_blade_A,    # Change blade here
#                         center_blade_A,
#                         center_blade_A,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         center_blade_B,
#                         center_blade_B,
#                         center_blade_B])
#
# coatings_BB = np.array([bottom_blade_A,    # Change blade here
#                         top_blade_A,
#                         bottom_blade_A,
#                         top_blade_A,
#                         bottom_blade_A,
#                         bottom_blade_A,    # Change blade here
#                         center_blade_A,
#                         center_blade_A,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         top_blade_B,
#                         bottom_blade_B,
#                         center_blade_B,
#                         center_blade_B,
#                         center_blade_B])
#
#
# eff_TT = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                    al_sub, coatings_TT, inclination)
# eff_CT = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                    al_sub, coatings_CT, inclination)
# eff_BT = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                    al_sub, coatings_BT, inclination)
#
# eff_TC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                    al_sub, coatings_TC, inclination)
# eff_CC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                    al_sub, coatings_CC, inclination)
# eff_BC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                    al_sub, coatings_BC, inclination)
#
# eff_TB = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                    al_sub, coatings_TB, inclination)
# eff_CB = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                    al_sub, coatings_CB, inclination)
# eff_BB = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                    al_sub, coatings_BB, inclination)
#
# fig = plt.figure()
# plt.plot(wavelengths, eff_TT, label='(1) Top-Top', linestyle='solid')
# plt.plot(wavelengths, eff_CT, label='(2) Center-Top', linestyle='dashed')
# plt.plot(wavelengths, eff_BT, label='(3) Bottom-Top', linestyle='dotted')
#
# plt.plot(wavelengths, eff_TC, label='(4) Top-Center', linestyle='solid')
# plt.plot(wavelengths, eff_CC, label='(5) Center-Center', linestyle='dashed')
# plt.plot(wavelengths, eff_BC, label='(6) Bottom-Center', linestyle='dotted')
#
# plt.plot(wavelengths, eff_TB, label='(7) Top-Bottom', linestyle='solid')
# plt.plot(wavelengths, eff_CB, label='(8) Center-Bottom', linestyle='dashed')
# plt.plot(wavelengths, eff_BB, label='(9) Bottom-Bottom', linestyle='dotted')
# plt.plot(wavelengths, ideal_efficiency, label='Optimized', linestyle='-.', color='black')
# plt.grid(True, which='major', linestyle='--', zorder=0)
# plt.grid(True, which='minor', linestyle='--', zorder=0)
# plt.xlabel('Wavelength (Å)')
# plt.ylabel('Efficiency')
# plt.legend(title='Configuration', loc=4)
# plt.title('Efficiency')
# plt.xlim(2, 20)
# plt.ylim(0, 1)
# fig.set_figheight(5)
# fig.set_figwidth(7)
# plt.savefig('../output/cspec_eff_average_efficiency_configurations.pdf')
# plt.show()
#
# fig = plt.figure()
# plt.plot(wavelengths, eff_TT - ideal_efficiency, label='(1) Top-Top', linestyle='solid')
# plt.plot(wavelengths, eff_CT - ideal_efficiency, label='(2) Center-Top', linestyle='dashed')
# plt.plot(wavelengths, eff_BT - ideal_efficiency, label='(3) Bottom-Top', linestyle='dotted')
#
# plt.plot(wavelengths, eff_TC - ideal_efficiency, label='(4) Top-Center', linestyle='solid')
# plt.plot(wavelengths, eff_CC - ideal_efficiency, label='(5) Center-Center', linestyle='dashed')
# plt.plot(wavelengths, eff_BC - ideal_efficiency, label='(6) Bottom-Center', linestyle='dotted')
#
# plt.plot(wavelengths, eff_TB - ideal_efficiency, label='(7) Top-Bottom', linestyle='solid')
# plt.plot(wavelengths, eff_CB - ideal_efficiency, label='(8) Center-Bottom', linestyle='dashed')
# plt.plot(wavelengths, eff_BB - ideal_efficiency, label='(9) Bottom-Bottom', linestyle='dotted')
# plt.grid(True, which='major', linestyle='--', zorder=0)
# plt.grid(True, which='minor', linestyle='--', zorder=0)
# plt.xlabel('Wavelength (Å)')
# plt.ylabel('Efficiency difference')
# plt.ylim(-0.02, 0.02)
# plt.xlim(2, 20)
# plt.legend(title='Configuration')
# plt.title('Efficiency difference: configuration - optimization')
# fig.set_figheight(5)
# fig.set_figwidth(7)
# plt.savefig('../output/cspec_eff_diff_average_efficiency_configurations.pdf')
# plt.show()


# ==============================================================================
#                   INVESTIGATION OF A SECOND SUGGESTION
# ==============================================================================

coatings_CC = np.array([center_blade_A,    # Change blade here
                        top_blade_A,
                        bottom_blade_A,
                        top_blade_A,
                        bottom_blade_A,
                        center_blade_A,    # Change blade here
                        center_blade_A,
                        center_blade_A,
                        top_blade_B,
                        bottom_blade_B,
                        top_blade_B,
                        bottom_blade_B,
                        top_blade_B,
                        bottom_blade_B,
                        center_blade_B,
                        center_blade_B,
                        center_blade_B])

coatings_BT = np.array([bottom_blade_A,    # Change blade here
                        top_blade_A,
                        bottom_blade_A,
                        top_blade_A,
                        bottom_blade_A,
                        top_blade_A,    # Change blade here
                        center_blade_A,
                        center_blade_A,
                        top_blade_B,
                        bottom_blade_B,
                        top_blade_B,
                        bottom_blade_B,
                        top_blade_B,
                        bottom_blade_B,
                        center_blade_B,
                        center_blade_B,
                        center_blade_B])

coatings_TB = np.array([top_blade_A,    # Change blade here
                        bottom_blade_A,
                        top_blade_A,
                        bottom_blade_A,
                        top_blade_A,
                        bottom_blade_A,    # Change blade here
                        center_blade_A,
                        center_blade_A,
                        top_blade_B,
                        bottom_blade_B,
                        top_blade_B,
                        bottom_blade_B,
                        top_blade_B,
                        bottom_blade_B,
                        center_blade_B,
                        center_blade_B,
                        center_blade_B])

coatings_TB2 = np.array([top_blade_A,    # Change blade here
                        top_blade_A,
                        bottom_blade_A,
                        top_blade_A,
                        bottom_blade_A,
                        bottom_blade_A,    # Change blade here
                        center_blade_A,
                        center_blade_A,
                        top_blade_B,
                        bottom_blade_B,
                        top_blade_B,
                        bottom_blade_B,
                        top_blade_B,
                        bottom_blade_B,
                        center_blade_B,
                        center_blade_B,
                        center_blade_B])

eff_CC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                   al_sub, coatings_CC, inclination)
eff_BT = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                   al_sub, coatings_BT, inclination)
eff_TB = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                   al_sub, coatings_TB, inclination)
eff_TB2 = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_TB2, inclination)

fig = plt.figure()
plt.plot(wavelengths, eff_CC, label='Version CC', linestyle='solid')
plt.plot(wavelengths, eff_BT, label='Version BT', linestyle='dashed')
#plt.plot(wavelengths, eff_TB2, label='Version TB(V2)', linestyle='dotted')
plt.plot(wavelengths, eff_TB, label='Version TB(V1)', linestyle='dotted')

plt.plot(wavelengths, ideal_efficiency, label='Optimized', linestyle='-.', color='black')
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency')
plt.legend(title='Configuration', loc=4)
plt.title('Efficiency')
plt.xlim(2, 20)
plt.ylim(0, 1)
fig.set_figheight(5)
fig.set_figwidth(7)
plt.savefig('../output/cspec_eff_average_efficiency_configurations_v1.pdf')

fig = plt.figure()
plt.plot(wavelengths, eff_CC - ideal_efficiency, label='Version CC', linestyle='solid')
plt.plot(wavelengths, eff_BT - ideal_efficiency, label='Version BT', linestyle='dashed')
plt.plot(wavelengths, eff_TB - ideal_efficiency, label='Version TB(V1)', linestyle='dotted')
#plt.plot(wavelengths, eff_TB2 - ideal_efficiency, label='Version TB(V2)', linestyle='dotted')

plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency difference')
plt.ylim(-0.02, 0.02)
plt.xlim(2, 20)
plt.legend(title='Configuration')
plt.title('Efficiency difference: configuration - optimization')
fig.set_figheight(5)
fig.set_figwidth(7)
plt.savefig('../output/cspec_eff_diff_average_efficiency_configurations_v1.pdf')
