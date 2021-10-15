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
import matplotlib.cm as cm

# ==============================================================================
#                                DEFINE PARAMETERS
# ==============================================================================

# General parameters
B10_object = B10.B10()
al_sub = 500 # um
inclination = 90
threshold = 120
ranges = B10_object.ranges(threshold, '10B4C 2.24g/cm3')
wavelengths_trex = np.linspace(0.7, 6.4, 100)
wavelengths_cspec = np.linspace(2, 20, 100)
coatings_ideal_trex = np.concatenate((np.ones(5) * 1,
                                      np.ones(10) * 1.25,
                                      np.ones(6) * 2))

coatings_ideal_cspec = np.concatenate((np.ones(7) * 0.5,
                                       np.ones(7) * 1,
                                       np.ones(3) * 1.5))

# ==============================================================================
#        COMPARE EFFICIENCY DROP TO EXTRA COATING IN FRONT OF BLADE
# ==============================================================================

eff_ideal_cspec = hf.get_efficiency_vs_lambda(wavelengths_cspec, ranges, B10_object,
                                              al_sub, coatings_ideal_cspec, inclination)

eff_ideal_trex = hf.get_efficiency_vs_lambda(wavelengths_trex, ranges, B10_object,
                                             al_sub, coatings_ideal_trex, inclination)

def get_eff_var(wavelengths, eff_ideal, B10_object, title):
    # Declare parameters
    thicknesses_in_um = np.arange(0.2, 1.3, 0.2)
    two_string_area_coverage = 0.183
    four_string_area_coverage = 0.133
    colors = cm.rainbow(np.linspace(0, 1, len(thicknesses_in_um)))

    # Get data
    ## Ax1
    eff_ax1 = []
    for thickness_in_um, color in zip(thicknesses_in_um, colors):
        abs = hf.get_absorption(B10_object, inclination, wavelengths, thickness_in_um)
        eff_temp = (1 - two_string_area_coverage * abs) * eff_ideal
        eff_ax1.append(eff_temp)

    ## Ax2
    eff_ax2 = []
    for thickness_in_um, color in zip(thicknesses_in_um, colors):
        abs = hf.get_absorption(B10_object, inclination, wavelengths, thickness_in_um)
        eff_temp = (1 - four_string_area_coverage * abs) * eff_ideal
        eff_ax2.append(eff_temp)

    ## Ax3
    eff_ax3 = []
    for thickness_in_um, color in zip(thicknesses_in_um, colors):
        abs = hf.get_absorption(B10_object, inclination, wavelengths, thickness_in_um)
        eff_temp = (1 - two_string_area_coverage * abs) * eff_ideal
        eff_ax3.append(eff_temp)

    eff_ax4 = []
    for thickness_in_um, color in zip(thicknesses_in_um, colors):
        abs = hf.get_absorption(B10_object, inclination, wavelengths, thickness_in_um)
        eff_temp = (1 - four_string_area_coverage * abs) * eff_ideal
        eff_ax4.append(eff_temp)

    # Plot
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharex='col', sharey='row')
    fig.set_figheight(10)
    fig.set_figwidth(10)
    plt.subplots_adjust(hspace=.03, wspace=.03)
    plt.suptitle(title)

    ## Ax1
    ax1.plot(wavelengths, eff_ideal, color='black', label='None')
    for eff, color, thickness_in_um in zip(eff_ax1, colors, thicknesses_in_um):
        ax1.plot(wavelengths, eff, color=color, label='%.1f um' % thickness_in_um)
    ax1.grid(True, which='major', linestyle='--', zorder=0)
    ax1.grid(True, which='minor', linestyle='--', zorder=0)
    ax1.set_ylabel('Efficiency')
    ax1.legend(title='Coating thickness')
    ax1.set_ylim(0, 1)
    ax1.set_title('2-string coating')

    ## Ax2
    ax2.plot(wavelengths, eff_ideal, color='black', label='Ideal')
    for eff, color, thickness_in_um in zip(eff_ax2, colors, thicknesses_in_um):
        ax2.plot(wavelengths, eff, color=color, label=None)
    ax2.grid(True, which='major', linestyle='--', zorder=0)
    ax2.grid(True, which='minor', linestyle='--', zorder=0)
    ax2.set_ylim(0, 1)
    ax2.set_title('4-string coating')

    ## Ax3
    for eff, color, thickness_in_um in zip(eff_ax3, colors, thicknesses_in_um):
        ax3.plot(wavelengths, eff-eff_ideal, color=color, label=None)
    ax3.grid(True, which='major', linestyle='--', zorder=0)
    ax3.grid(True, which='minor', linestyle='--', zorder=0)
    ax3.set_xlabel('Wavelength (Å)')
    ax3.set_ylim(-0.1, 0)
    ax3.axhline(-0.01, color='grey', linestyle='--')
    ax3.set_ylabel('Efficiency difference (real-ideal)')

    ## Ax4
    for eff, color, thickness_in_um in zip(eff_ax4, colors, thicknesses_in_um):
        ax4.plot(wavelengths, eff-eff_ideal, color=color, label=None)
    ax4.grid(True, which='major', linestyle='--', zorder=0)
    ax4.grid(True, which='minor', linestyle='--', zorder=0)
    ax4.set_xlabel('Wavelength (Å)')
    ax4.set_ylim(-0.1, 0)
    ax4.axhline(-0.01, color='grey', linestyle='--')

    fig.set_figheight(10)
    fig.set_figwidth(10)
    plt.savefig('../output/%s_eff_variance.pdf' % title)
    

def get_abs(wavelengths, B10_object, title):
    # Declare parameters
    thicknesses_in_um = np.arange(0.2, 1.3, 0.2)
    colors = cm.rainbow(np.linspace(0, 1, len(thicknesses_in_um)))
    # Get data
    absorptions = []
    for thickness_in_um in thicknesses_in_um:
        abs = hf.get_absorption(B10_object, inclination, wavelengths, thickness_in_um)
        absorptions.append(abs)
    # Plot
    fig = plt.figure()
    for absorption, thickness_in_um, color in zip(absorptions, thicknesses_in_um, colors):
        plt.plot(wavelengths, absorption, color=color, label='%.1f um' % thickness_in_um)
    plt.grid(True, which='major', linestyle='--', zorder=0)
    plt.grid(True, which='minor', linestyle='--', zorder=0)
    plt.ylabel('Absorption')
    plt.legend(title='Coating thickness')
    #plt.xlim(0, 20)
    plt.ylim(0.001, 1)
    plt.yscale('log')
    plt.title(title)
    plt.savefig('../output/%s_absorption.pdf' % title)



get_eff_var(wavelengths_trex, eff_ideal_trex, B10_object, 'T-REX')
get_eff_var(wavelengths_cspec, eff_ideal_cspec, B10_object, 'CSPEC')

get_abs(wavelengths_trex, B10_object, 'T-REX')
get_abs(wavelengths_cspec, B10_object, 'CSPEC')


# ==============================================================================
#                COMPARE EFFICIENCY DROP IF ONE BLADE LESS
# ==============================================================================

coatings_no_single_blade_trex = np.concatenate((np.ones(4) * 1,
                                                np.ones(10) * 1.25,
                                                np.ones(6) * 2))

coatings_no_single_blade_cspec = np.concatenate((np.ones(6) * 0.5,
                                                 np.ones(7) * 1,
                                                 np.ones(3) * 1.5))

eff_no_single_blade_trex = hf.get_efficiency_vs_lambda_no_single_blade(wavelengths_trex, ranges, B10_object,
                                                                       al_sub, coatings_no_single_blade_trex, inclination)

eff_no_single_blade_cspec = hf.get_efficiency_vs_lambda_no_single_blade(wavelengths_cspec, ranges, B10_object,
                                                                        al_sub, coatings_no_single_blade_cspec, inclination)



def compare_no_1_side_blade(wavelengths, eff_ideal, eff_no_single_blade, B10_object, title):
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex='col', sharey='row')
    #fig.suptitle('Figure-of-merits at %.3f eV' % energy, y=.99)
    fig.set_figheight(10)
    fig.set_figwidth(6)
    plt.subplots_adjust(hspace=.03, wspace=.03)
    ax1.plot(wavelengths, eff_no_single_blade, label='Without 1-side coated blade')
    ax1.plot(wavelengths, eff_ideal, label='With 1-side coated blade')
    ax1.grid(True, which='major', linestyle='--', zorder=0)
    ax1.grid(True, which='minor', linestyle='--', zorder=0)
    ax1.set_ylabel('Efficiency')
    ax1.set_title(title)
    ax1.legend(title='Configuration')
    ax1.set_ylim(0, 1)

    ax2.plot(wavelengths, eff_no_single_blade - eff_ideal, color='black')
    ax2.grid(True, which='major', linestyle='--', zorder=0)
    ax2.grid(True, which='minor', linestyle='--', zorder=0)
    ax2.set_xlabel('Wavelength (Å)')
    ax2.set_ylabel('Efficiency difference')
    ax2.set_ylim(-0.1, 0)
    ax2.axhline(-0.01, color='grey', linestyle='--')

    plt.tight_layout()

    plt.savefig('../output/%s_single_coated_blade_difference.pdf' % title)


compare_no_1_side_blade(wavelengths_trex, eff_ideal_trex, eff_no_single_blade_trex, B10_object, 'T-REX')
compare_no_1_side_blade(wavelengths_cspec, eff_ideal_cspec, eff_no_single_blade_cspec, B10_object, 'CSPEC')

# ==============================================================================
#                           GET EFFICIENCY PER LAYER
# ==============================================================================

def plot_eff_per_layer(wavelengths, ranges, B10_object, al_sub, coatings,
                      coatings_1_side, inclination, title):
    layers = []
    layers.append(coatings[0])
    for i, coating in enumerate(coatings[1:-1]):
        layers.append(coating)
        layers.append(coating)
    layers.append(coatings[-1])
    layers = np.array(layers)
    print(layers)
    layers = np.arange(1, 2*(len(coatings)-2) + 3, 1)


    for wavelength in wavelengths:
        print('tjenare')
        eff_vec = hf.get_efficiency_per_layer(wavelength, ranges, B10_object, al_sub, coatings, inclination)
        eff_vec_no_1_side_blade = hf.get_eff_per_layer_no_single_blade(wavelength, ranges, B10_object, al_sub, coatings_1_side, inclination)
        fig = plt.figure()
        print('hej')
        print(len(eff_vec))
        print(len(layers))
        plt.bar(layers, eff_vec, color='grey', edgecolor='blue', zorder=10,
                width=0.5, label='With 1-side blade (Efficiency: %.3f)' % sum(eff_vec), alpha=0.8)
        plt.bar(layers[:-1], eff_vec_no_1_side_blade, color='grey', edgecolor='red',
                zorder=10, width=0.5, label='Without 1-side blade (Efficiency: %.3f)' % sum(eff_vec_no_1_side_blade), alpha=0.8)
        plt.grid(True, which='major', linestyle='--', zorder=0)
        plt.grid(True, which='minor', linestyle='--', zorder=0)
        plt.xlabel('Layer')
        plt.ylabel('Efficiency')
        plt.legend(title='Configuration')
        plt.ylim(0, 0.17)
        #plt.axhline(0.01, color='grey', linestyle='--')
        plt.title(title + ', %.2f Å\nEfficiency difference: %.3f' % (wavelength, sum(eff_vec)-sum(eff_vec_no_1_side_blade)))
        plt.savefig('../output/%s_eff_per_layer_%.2f_Å.pdf' % (title, wavelength))
        plt.close()

wavelengths_trex_short = np.linspace(0.7, 6.4, 4)
plot_eff_per_layer(wavelengths_trex_short, ranges, B10_object, al_sub,
                   coatings_ideal_trex, coatings_no_single_blade_trex, inclination, 'T-REX')
wavelengths_cspec_short = np.linspace(2, 20, 4)
plot_eff_per_layer(wavelengths_cspec_short, ranges, B10_object, al_sub,
                   coatings_ideal_cspec, coatings_no_single_blade_cspec, inclination, 'CSPEC')
