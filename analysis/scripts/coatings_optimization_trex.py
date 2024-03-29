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
wavelengths = np.linspace(0.7, 7, 100)
coatings_ideal = np.concatenate((np.ones(5) * 1,
                                 np.ones(10) * 1.25,
                                 np.ones(6) * 2))

# Blade positions relative to triple blade center (cm)
middle_blade_1 = -7.325
middle_blade_2 = 7.325
upper_blade_1 = 7.925
upper_blade_2 = 22.575
lower_blade_1 = -22.575
lower_blade_2 = -7.925


# ==============================================================================
#                            GET THICKNESS DISTRIBUTION
# ==============================================================================

xx = np.linspace(-25, 25, 200)
yy = hf.get_triple_blade_thickness_distribution(xx)
# Get blade positions
middle_blade_1 = -7.325
middle_blade_2 = 7.325
upper_blade_1 = 7.925
upper_blade_2 = 22.575
lower_blade_1 = -22.575
lower_blade_2 = -7.925
fig = plt.figure()
plt.plot(xx, yy, label='Thickness', color='black')
plt.fill_betweenx([0, 1], middle_blade_1, middle_blade_2, color='blue',
                  alpha=0.3, label='Middle blade')
plt.fill_betweenx([0, 1], upper_blade_1, upper_blade_2, color='red',
                  alpha=0.3, label='Upper blade')
plt.fill_betweenx([0, 1], lower_blade_1, lower_blade_2, color='green',
                  alpha=0.3, label='Lower blade')
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Triple blade position (cm)')
plt.ylabel('Relative thickness')
plt.legend()
plt.xlim(-25, 25)
plt.ylim(min(yy), 1)
plt.title('Thickness relative to center of Triple blade')
plt.savefig('../output/trex_triple_blade_thickness_distribution.pdf')
plt.close()


# ==============================================================================
#              INVESTGATE WHAT HAPPENS IF FIRST COATING IS REMOVED
# ==============================================================================

coatings_no_single_blade = np.concatenate((np.ones(4) * 1,
                                           np.ones(10) * 1.25,
                                           np.ones(6) * 2))

eff_no_single_blade = hf.get_efficiency_vs_lambda_no_single_blade(wavelengths, ranges, B10_object,
                                                                  al_sub, coatings_no_single_blade, inclination)

eff_ideal = hf.get_efficiency_vs_lambda(wavelengths, ranges, B10_object,
                                        al_sub, coatings_ideal, inclination)


fig = plt.figure()
plt.plot(wavelengths, eff_no_single_blade, label='Without single-coated')
plt.plot(wavelengths, eff_ideal, label='With single-coated')
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency')
plt.title('Efficiency comparison, with and without first single coated blade')
plt.legend(title='Configuration')
plt.savefig('../output/trex_single_coated_blade.pdf')
plt.tight_layout()
plt.close()

fig = plt.figure()
plt.plot(wavelengths, eff_no_single_blade - eff_ideal, color='black')
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency difference')
plt.title('"Without first single-coated blade" - "With first single-coated blade"')
plt.tight_layout()
plt.savefig('../output/trex_single_coated_blade_difference.pdf')
plt.close()



# ==============================================================================
#              GET EFFICIENCY ACCOUNTING FOR THICKNESS VARIATION
# ==============================================================================

# Define number of data points
number_data_points = 5
# Get points along the blades
middle_blade_points = np.linspace(middle_blade_1, middle_blade_2, number_data_points)
upper_blade_points = np.linspace(upper_blade_1, upper_blade_2, number_data_points)
lower_blade_points = np.linspace(lower_blade_1, lower_blade_2, number_data_points)
# Get corresponding thicknesses along the blade
middle_blade_relative = hf.get_triple_blade_thickness_distribution(middle_blade_points)
upper_blade_relative = hf.get_triple_blade_thickness_distribution(upper_blade_points)
lower_blade_relative = hf.get_triple_blade_thickness_distribution(lower_blade_points)
# Declare aimed thicknesses (um)
section_A = 1.2
section_B = 2.5
# Declare coatings thicknesses
middle_blade_A = section_A * middle_blade_relative
upper_blade_A = section_A * upper_blade_relative
lower_blade_A = section_A * lower_blade_relative
middle_blade_B = section_B * middle_blade_relative
upper_blade_B = section_B * upper_blade_relative
lower_blade_B = section_B * lower_blade_relative
# Declare coating configuration
coatings_vec = np.array([middle_blade_A,
                         lower_blade_A, upper_blade_A,
                         lower_blade_A, upper_blade_A,
                         lower_blade_A, upper_blade_A,
                         lower_blade_A, upper_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         lower_blade_B, upper_blade_B,
                         lower_blade_B, upper_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])
# Get average efficiency across blade
average_efficiency = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                               al_sub, coatings_vec, inclination)
# Get efficiency for 80% thickness approximation
coatings_approx = np.concatenate((np.ones(1) * section_A,
                                  np.ones(8) * section_A*0.8,
                                  np.ones(4) * section_A,
                                  np.ones(4) * section_B*0.8,
                                  np.ones(2) * section_B,
                                  np.ones(2) * section_B))
approx_efficiency = hf.get_efficiency_vs_lambda(wavelengths, ranges, B10_object,
                                                al_sub, coatings_approx, inclination)
# Compare results
fig = plt.figure()
plt.plot(wavelengths, average_efficiency, label='Averaged over blade')
plt.plot(wavelengths, approx_efficiency, label='80% approximation')
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency')
plt.title('Efficiency')
plt.legend(title='Configuration')
plt.tight_layout()
plt.savefig('../output/trex_average_efficiency_vs_80_percent_approximation.pdf')
plt.close()

fig = plt.figure()
plt.plot(wavelengths, average_efficiency - approx_efficiency, color='black')
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency difference')
plt.title('"Averaged efficiency over blade" - "80% approximation"')
plt.tight_layout()
plt.savefig('../output/trex_average_efficiency_vs_80_percent_approximation_difference.pdf')
plt.close()



# ==============================================================================
#                   INVESTIGATION OF SUGGESTED CONFIGURATIONS
# ==============================================================================

ideal_efficiency = hf.get_efficiency_vs_lambda(wavelengths, ranges, B10_object,
                                               al_sub, coatings_ideal, inclination)
# Define number of data points
number_data_points = 5
# Get points along the blades
middle_blade_points = np.linspace(middle_blade_1, middle_blade_2, number_data_points)
upper_blade_points = np.linspace(upper_blade_1, upper_blade_2, number_data_points)
lower_blade_points = np.linspace(lower_blade_1, lower_blade_2, number_data_points)
# Get corresponding thicknesses along the blade
middle_blade_relative = hf.get_triple_blade_thickness_distribution(middle_blade_points)
upper_blade_relative = hf.get_triple_blade_thickness_distribution(upper_blade_points)
lower_blade_relative = hf.get_triple_blade_thickness_distribution(lower_blade_points)
# Declare aimed thicknesses (um)
section_A = 1.2
section_B = 2.0
# Declare coatings thicknesses
middle_blade_A = section_A * middle_blade_relative
upper_blade_A = section_A * upper_blade_relative
lower_blade_A = section_A * lower_blade_relative
middle_blade_B = section_B * middle_blade_relative
upper_blade_B = section_B * upper_blade_relative
lower_blade_B = section_B * lower_blade_relative
# Declare coating configuration alternatives
coatings_CCC = np.array([middle_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         middle_blade_A, middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_TTB = np.array([upper_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_BTB = np.array([lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_TBC = np.array([upper_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         lower_blade_A, middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_BTC = np.array([lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_CTB = np.array([middle_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_TBC = np.array([upper_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         lower_blade_A, middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_CBC = np.array([middle_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         lower_blade_A, middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_BBC = np.array([lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         lower_blade_A, middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_TTT = np.array([upper_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, upper_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_CTT = np.array([middle_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, upper_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_BTT = np.array([lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, upper_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_TCC = np.array([upper_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         middle_blade_A, middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

coatings_BCC = np.array([lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         upper_blade_A, lower_blade_A,
                         middle_blade_A, middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         middle_blade_A,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         upper_blade_B, lower_blade_B,
                         middle_blade_B,
                         middle_blade_B,
                         middle_blade_B])

eff_CCC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_CCC, inclination)
eff_TTB = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_TTB, inclination)
eff_BTB = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_BTB, inclination)
eff_TBC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_TBC, inclination)
eff_BTC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_BTC, inclination)
eff_CTB = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_CTB, inclination)

fig = plt.figure()
plt.plot(wavelengths, eff_TBC, label='(1) Top-Bottom-Center', linestyle='solid')
plt.plot(wavelengths, eff_BTC, label='(2) Bottom-Top-Center', linestyle='dashed')
plt.plot(wavelengths, eff_CTB, label='(3) Center-Top-Bottom', linestyle='dotted')
plt.plot(wavelengths, ideal_efficiency, label='Optimized', linestyle='-.', color='black')
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency')
plt.legend(title='Configuration', loc=4)
plt.title('Efficiency')
plt.xlim(0.7, 6.4)
plt.ylim(0, 1)
fig.set_figheight(5)
fig.set_figwidth(7)
plt.savefig('../output/trex_eff_average_efficiency_configurations.pdf')

fig = plt.figure()
plt.plot(wavelengths, eff_TBC - ideal_efficiency,
         label='(1) Top-Bottom-Center', linestyle='solid')
plt.plot(wavelengths, eff_BTC - ideal_efficiency,
         label='(2) Bottom-Top-Center', linestyle='dashed')
plt.plot(wavelengths, eff_CTB - ideal_efficiency,
         label='(3) Center-Top-Bottom', linestyle='dotted')
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency difference')
plt.ylim(-0.01, 0.01)
plt.xlim(0.7, 6.4)
plt.legend(title='Configuration')
plt.title('Efficiency difference: configuration - optimization')
fig.set_figheight(5)
fig.set_figwidth(7)
plt.savefig('../output/trex_eff_diff_average_efficiency_configurations.pdf')

############################################################
### Investigation to see if versions can be reduced to 2 ###
############################################################

# eff_TBC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                     al_sub, coatings_TBC, inclination)
# eff_CBC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                     al_sub, coatings_CBC, inclination)
# eff_BBC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                     al_sub, coatings_BBC, inclination)
#
# eff_TTT = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                     al_sub, coatings_TTT, inclination)
# eff_CTT = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                     al_sub, coatings_CTT, inclination)
# eff_BTT = hf.get_average_efficiency(wavelengths, ranges, B10_object,
#                                     al_sub, coatings_BTT, inclination)
#
# fig = plt.figure()
# plt.plot(wavelengths, eff_TBC, label='(1) Top-Bottom-Center', linestyle='solid')
# plt.plot(wavelengths, eff_BBC, label='(2) Bottom-Bottom-Center', linestyle='dashed')
# plt.plot(wavelengths, eff_CBC, label='(3) Center-Bottom-Center', linestyle='dotted')
# plt.plot(wavelengths, eff_TTT, label='(4) Top-Top-Top', linestyle='solid')
# plt.plot(wavelengths, eff_BTT, label='(5) Bottom-Top-Top', linestyle='dashed')
# plt.plot(wavelengths, eff_CTT, label='(6) Center-Top-Top', linestyle='dotted')
# plt.plot(wavelengths, ideal_efficiency, label='Optimized', linestyle='-.', color='black')
# plt.grid(True, which='major', linestyle='--', zorder=0)
# plt.grid(True, which='minor', linestyle='--', zorder=0)
# plt.xlabel('Wavelength (Å)')
# plt.ylabel('Efficiency')
# plt.xlim(0.7, 6.4)
# plt.ylim(0, 1)
# plt.legend(title='Configuration', loc=4)
# plt.title('Efficiency')
# plt.savefig('../output/trex_eff_average_efficiency_configurations_v2.pdf')
#
# fig = plt.figure()
# plt.plot(wavelengths, eff_TBC - ideal_efficiency,
#          label='(1) Top-Bottom-Center', linestyle='solid')
# plt.plot(wavelengths, eff_BBC - ideal_efficiency,
#          label='(2) Bottom-Bottom-Center', linestyle='dashed')
# plt.plot(wavelengths, eff_CBC - ideal_efficiency,
#          label='(3) Center-Bottom-Center', linestyle='dotted')
# plt.plot(wavelengths, eff_TTT - ideal_efficiency,
#          label='(4) Top-Top-Top', linestyle='solid')
# plt.plot(wavelengths, eff_BTT - ideal_efficiency,
#          label='(5) Bottom-Top-Top', linestyle='dashed')
# plt.plot(wavelengths, eff_CTT - ideal_efficiency,
#          label='(6) Center-Top-Top', linestyle='dotted')
# plt.grid(True, which='major', linestyle='--', zorder=0)
# plt.grid(True, which='minor', linestyle='--', zorder=0)
# plt.xlabel('Wavelength (Å)')
# plt.ylabel('Efficiency difference')
# plt.ylim(-0.01, 0.01)
# plt.xlim(0.7, 6.4)
# plt.legend(title='Configuration')
# plt.title('Efficiency difference: configuration - optimization')
# plt.savefig('../output/trex_eff_diff_average_efficiency_configurations_v2.pdf')

########################################################################
### Investigation to see if versions can be reduced to 2 (ATTEMPT 2) ###
########################################################################

eff_TTB = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_TTB, inclination)
eff_CTB = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_CTB, inclination)
eff_BTB = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_BTB, inclination)

eff_TCC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_TCC, inclination)
eff_CCC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_CCC, inclination)
eff_BCC = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                    al_sub, coatings_BCC, inclination)

fig = plt.figure()
plt.plot(wavelengths, eff_TTB, label='(1) Top-Top-Bottom', linestyle='solid')
plt.plot(wavelengths, eff_BTB, label='(2) Bottom-Top-Bottom', linestyle='dashed')
plt.plot(wavelengths, eff_CTB, label='(3) Center-Top-Bottom', linestyle='dotted')

plt.plot(wavelengths, eff_TCC, label='(4) Top-Center-Center', linestyle='solid')
plt.plot(wavelengths, eff_BCC, label='(5) Bottom-Center-Center', linestyle='dashed')
plt.plot(wavelengths, eff_CCC, label='(6) Center-Center-Center', linestyle='dotted')
plt.plot(wavelengths, ideal_efficiency, label='Optimized', linestyle='-.', color='black')
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency')
plt.xlim(0.7, 6.4)
plt.ylim(0, 1)
plt.legend(title='Configuration', loc=4)
plt.tight_layout()
plt.title('Efficiency')
fig.set_figheight(5)
fig.set_figwidth(7)
plt.savefig('../output/trex_eff_average_efficiency_configurations_v3.pdf')

fig = plt.figure()
plt.plot(wavelengths, eff_TTB - ideal_efficiency,
         label='(1) Top-Top-Bottom', linestyle='solid')
plt.plot(wavelengths, eff_BTB - ideal_efficiency,
         label='(2) Bottom-Top-Bottom', linestyle='dashed')
plt.plot(wavelengths, eff_CTB - ideal_efficiency,
         label='(3) Center-Top-Bottom', linestyle='dotted')
plt.plot(wavelengths, eff_TCC - ideal_efficiency,
         label='(4) Top-Center-Center', linestyle='solid')
plt.plot(wavelengths, eff_BCC - ideal_efficiency,
         label='(5) Bottom-Center-Center', linestyle='dashed')
plt.plot(wavelengths, eff_CCC - ideal_efficiency,
         label='(6) Center-Center-Center', linestyle='dotted')
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency difference')
plt.ylim(-0.01, 0.01)
plt.xlim(0.7, 6.4)
plt.legend(title='Configuration')
plt.title('Efficiency difference: configuration - optimization')
plt.tight_layout()
fig.set_figheight(5)
fig.set_figwidth(7)
plt.savefig('../output/trex_eff_diff_average_efficiency_configurations_v3.pdf')


####################
### Suggestion 1 ###
####################

options_1 = [[lower_blade_A, 'bottom'],
             [middle_blade_A, 'center'],
             [upper_blade_A, 'upper']]
options_2 = [[upper_blade_A, 'upper']]
options_3 = [[upper_blade_A, 'upper']]
orientations = ['lower', 'middle', 'upper']
permutations = len(options_1) * len(options_2) * len(options_3)
# Iterate through all permutations
progress = 0
average_efficiencies = []
labels = []
for a, option_1_vec in enumerate(options_1):
    for b, option_2_vec in enumerate(options_2):
        for c, option_3_vec in enumerate(options_3):
            option_1, label_1 = option_1_vec
            option_2, label_2 = option_2_vec
            option_3, label_3 = option_3_vec
            print('Progress: %d/%d' % (progress, permutations))
            progress += 1
            coatings_per = np.array([option_1,
                                     lower_blade_A, upper_blade_A,
                                     lower_blade_A, upper_blade_A,
                                     lower_blade_A, upper_blade_A,
                                     option_2, option_3,
                                     middle_blade_A,
                                     middle_blade_A,
                                     middle_blade_A,
                                     lower_blade_B, upper_blade_B,
                                     lower_blade_B, upper_blade_B,
                                     lower_blade_B, upper_blade_B,
                                     middle_blade_B,
                                     middle_blade_B,
                                     middle_blade_B])
            average_efficiency = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                                           al_sub, coatings_per, inclination)
            labels.append('[%s, %s, %s]' % (label_1, label_2, label_3))
            average_efficiencies.append(average_efficiency)

## Absolute values
fig = plt.figure()
plt.plot(wavelengths, ideal_efficiency, label='Optimization', color='black')
for average_efficiency, label in zip(average_efficiencies, labels):
    plt.plot(wavelengths, average_efficiency, label=label)
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency')
plt.legend(title='Permutation')
plt.title('Suggestion 1: All permutations')
plt.tight_layout()
plt.savefig('../output/trex_average_efficiency_suggestion_1.pdf')
plt.close()
## Differences
fig = plt.figure()
for average_efficiency, label in zip(average_efficiencies, labels):
    plt.plot(wavelengths, average_efficiency-ideal_efficiency, label=label)
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency difference')
plt.ylim(-0.01, 0.01)
plt.legend(title='Permutation')
plt.title('Suggestion 1: All permutations (difference: permutation - ideal)')
plt.tight_layout()
plt.savefig('../output/trex_average_efficiency_suggestion_1_diff.pdf')
plt.close()

####################
### Suggestion 2 ###
####################

options_1 = [middle_blade_A, upper_blade_A]
options_2 = [middle_blade_A, lower_blade_A]
options_3 = [middle_blade_B, upper_blade_B]
# Iterate through all permutations
progress = 0
average_efficiencies = []
labels = []
for a, option_1 in enumerate(options_1):
    for b, option_2 in enumerate(options_2):
        for c, option_3 in enumerate(options_3):
            print('%d/7' % progress)
            progress += 1
            coatings_per = np.array([option_1,
                                     lower_blade_A, upper_blade_A,
                                     lower_blade_A, upper_blade_A,
                                     lower_blade_A, upper_blade_A,
                                     option_2,
                                     middle_blade_A,
                                     middle_blade_A,
                                     middle_blade_A,
                                     lower_blade_B, upper_blade_B,
                                     lower_blade_B, upper_blade_B,
                                     lower_blade_B, upper_blade_B,
                                     option_3,
                                     middle_blade_B,
                                     middle_blade_B,
                                     middle_blade_B])
            average_efficiency = hf.get_average_efficiency(wavelengths, ranges, B10_object,
                                                           al_sub, coatings_per, inclination)
            average_efficiencies.append(average_efficiency)
            labels.append('[%d, %d, %d]' % (a, b, c))

## Absolute values
fig = plt.figure()
plt.plot(wavelengths, ideal_efficiency, label='Optimization', color='black')
for average_efficiency, label in zip(average_efficiencies, labels):
    plt.plot(wavelengths, average_efficiency, label=label)
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency')
plt.legend(title='Permutation')
plt.title('Suggestion 2: All permutations')
plt.tight_layout()
plt.savefig('../output/trex_average_efficiency_suggestion_2.pdf')
plt.close()
## Differences
fig = plt.figure()
for average_efficiency, label in zip(average_efficiencies, labels):
    plt.plot(wavelengths, average_efficiency-ideal_efficiency, label=label)
plt.grid(True, which='major', linestyle='--', zorder=0)
plt.grid(True, which='minor', linestyle='--', zorder=0)
plt.xlabel('Wavelength (Å)')
plt.ylabel('Efficiency difference')
plt.legend(title='Permutation')
plt.title('Suggestion 2: All permutations (difference: permutation - ideal)')
plt.tight_layout()
plt.savefig('../output/trex_average_efficiency_suggestion_2_diff.pdf')
plt.close()
