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
import os

def get_varargin(al_sub, wavelength, inclination):
    """ Calculates the transmission through aluminum at a specific aluminum
        thickness, inclination, and wavelength.

        Args:
            al_sub (int): Aluminum substrate thickness in um
            wavelength (np.array): Wavelength in unit angstrom
            inclination (int): Incident neutron angle on the blades, 90 degrees
                               is for neutrons hitting perpendicularly.
        Returns:
            varargin (float): Transmission through the aluminum, a number
                              between 0 and 1.
    """
    varargin = Aluminium.aluminium(al_sub, [[wavelength]], inclination)[0]
    return varargin

def get_sigma_eq(wavelength, inclination, B10_object):
    """ Calculates the equivalent sigma, i.e accounting for wavelength,
        inclination and density.

        Args:
            wavelength (np.array): Wavelength in unit angstrom
            inclination (int): Incident neutron angle on the blades, 90 degrees
                               is for neutrons hitting perpendicularly.
            B10_object (B10): Object to calculate interaction cross-sections

        Returns:
            sigma_eq (float): Equivalent sigma at the specified inclination
                              and wavelength
    """
    cross_section = B10_object.read_cross_section([[wavelength]])
    macro_cross_section = B10_object.macro_sigma(cross_section)
    sigma_eq = B10_object.sigma_eq(macro_cross_section, inclination)[0]
    return sigma_eq

def get_efficiency(wavelength, ranges, B10_object, al_sub, coatings, inclination):
    """ Calculates the efficiency for a specific configuration of
        blades, where the first blade is single-coated and the last blade only
        contributes to efficiency from back-scattering.

        Args:
            wavelengths (np.array): Wavelengths in unit angstrom
            ranges (list): Ranges of the alpha and Li-6 ions, for both branches
            B10_object (B10): Object to calculate interaction cross-sections
            al_sub (int): Aluminum substrate thickness in um
            coatings (np.array): Array containing blade coating thicknesses
            inclination (int): Incident neutron angle on the blades, 90 degrees
                               is for neutrons hitting perpendicularly.
        Returns:
            efficiency_array (np.array): Efficiency for the configuration
    """
    # Get parameters
    varargin = get_varargin(al_sub, wavelength, inclination)
    sigma_eq = get_sigma_eq(wavelength, inclination, B10_object)
    # Iterate through coatings (first blade only forward, last only backwards)
    cum_thick = 0
    cum_eff = 0
    for i, thickness in enumerate(coatings):
        eff = efftools.efficparam(thickness, sigma_eq, ranges, varargin)
        back_scattering, transmission = eff[0], eff[1]
        if i == 0:
            cum_eff += varargin * transmission
            cum_thick += thickness
        elif i == len(coatings)-1:
            cum_eff += (varargin ** i) * np.exp(-cum_thick*sigma_eq) * back_scattering
        else:
            eff_back = (varargin ** i) * np.exp(-cum_thick*sigma_eq) * back_scattering
            eff_trans = (varargin ** (i+1)) * np.exp(-(cum_thick+thickness)*sigma_eq) * transmission
            cum_eff += (eff_back + eff_trans)
            cum_thick += 2*thickness
    efficiency = cum_eff
    return efficiency

def get_efficiency_per_layer(wavelength, ranges, B10_object, al_sub, coatings, inclination):
    """ Calculates the efficiency per layer for a specific configuration of
        blades, where the first blade is single-coated and the last blade only
        contributes to efficiency from back-scattering.

        Args:
            wavelengths (np.array): Wavelengths in unit angstrom
            ranges (list): Ranges of the alpha and Li-6 ions, for both branches
            B10_object (B10): Object to calculate interaction cross-sections
            al_sub (int): Aluminum substrate thickness in um
            coatings (np.array): Array containing blade coating thicknesses
            inclination (int): Incident neutron angle on the blades, 90 degrees
                               is for neutrons hitting perpendicularly.
        Returns:
            efficiency_array (np.array): Efficiency for the configuration
    """
    # Get parameters
    varargin = get_varargin(al_sub, wavelength, inclination)
    sigma_eq = get_sigma_eq(wavelength, inclination, B10_object)
    # Iterate through coatings (first blade only forward, last only backwards)
    cum_thick = 0
    cum_eff = 0
    eff_vec = []
    for i, thickness in enumerate(coatings):
        eff = efftools.efficparam(thickness, sigma_eq, ranges, varargin)
        back_scattering, transmission = eff[0], eff[1]
        if i == 0:
            eff_vec.append(varargin * transmission)
            cum_thick += thickness
        elif i == len(coatings)-1:
            eff_vec.append((varargin ** i) * np.exp(-cum_thick*sigma_eq) * back_scattering)
        else:
            eff_vec.append((varargin ** i) * np.exp(-cum_thick*sigma_eq) * back_scattering)
            eff_vec.append((varargin ** (i+1)) * np.exp(-(cum_thick+thickness)*sigma_eq) * transmission)
            cum_thick += 2*thickness
    eff_vec_np = np.array(eff_vec)
    return eff_vec_np

def get_efficiency_no_single_blade(wavelength, ranges, B10_object, al_sub, coatings, inclination):
    """ Calculates the efficiency for a specific configuration of
        blades, where the coating on the first blade is missing.

        Args:
            wavelengths (np.array): Wavelengths in unit angstrom
            ranges (list): Ranges of the alpha and Li-6 ions, for both branches
            B10_object (B10): Object to calculate interaction cross-sections
            al_sub (int): Aluminum substrate thickness in um
            coatings (np.array): Array containing blade coating thicknesses
            inclination (int): Incident neutron angle on the blades, 90 degrees
                               is for neutrons hitting perpendicularly.
        Returns:
            efficiency (np.array): Efficiency for the configuration
    """
    # Get parameters
    varargin = get_varargin(al_sub, wavelength, inclination)
    sigma_eq = get_sigma_eq(wavelength, inclination, B10_object)
    # Iterate through coatings (first blade is only transmission, last blade on back)
    cum_thick = 0
    cum_eff = 0
    for i, thickness in enumerate(coatings):
        eff = efftools.efficparam(thickness, sigma_eq, ranges, varargin)
        back_scattering, transmission = eff[0], eff[1]
        if i == len(coatings)-1:
            cum_eff += (varargin ** (i+1)) * np.exp(-cum_thick*sigma_eq) * back_scattering
        else:
            eff_back = (varargin ** (i+1)) * np.exp(-cum_thick*sigma_eq) * back_scattering
            eff_trans = (varargin ** (i+2)) * np.exp(-(cum_thick+thickness)*sigma_eq) * transmission
            cum_eff += (eff_back + eff_trans)
            cum_thick += 2*thickness
    efficiency = cum_eff
    return efficiency

def get_eff_per_layer_no_single_blade(wavelength, ranges, B10_object, al_sub, coatings, inclination):
    """ Calculates the efficiency per layer for a specific configuration of
        blades, where the coating on the first blade is missing.

        Args:
            wavelengths (np.array): Wavelengths in unit angstrom
            ranges (list): Ranges of the alpha and Li-6 ions, for both branches
            B10_object (B10): Object to calculate interaction cross-sections
            al_sub (int): Aluminum substrate thickness in um
            coatings (np.array): Array containing blade coating thicknesses
            inclination (int): Incident neutron angle on the blades, 90 degrees
                               is for neutrons hitting perpendicularly.
        Returns:
            efficiency (np.array): Efficiency for the configuration
    """
    # Get parameters
    varargin = get_varargin(al_sub, wavelength, inclination)
    sigma_eq = get_sigma_eq(wavelength, inclination, B10_object)
    # Iterate through coatings (first blade is only transmission, last blade on back)
    cum_thick = 0
    cum_eff = 0
    eff_vec = []
    for i, thickness in enumerate(coatings):
        eff = efftools.efficparam(thickness, sigma_eq, ranges, varargin)
        back_scattering, transmission = eff[0], eff[1]
        if i == len(coatings)-1:
            eff_vec.append((varargin ** (i+1)) * np.exp(-cum_thick*sigma_eq) * back_scattering)
        else:
            eff_vec.append((varargin ** (i+1)) * np.exp(-cum_thick*sigma_eq) * back_scattering)
            eff_vec.append((varargin ** (i+2)) * np.exp(-(cum_thick+thickness)*sigma_eq) * transmission)
            cum_thick += 2*thickness
    eff_vec_np = np.array(eff_vec)
    return eff_vec_np

def get_efficiency_vs_lambda(wavelengths, ranges, B10_object, al_sub, coatings, inclination):
    """ Calculates the efficiency vs lambda for a specific configuration of
        blades, where the first blade is single-coated and the last blade only
        contributes to efficiency from back-scattering.

        Args:
            wavelengths (np.array): Wavelengths in unit angstrom
            ranges (list): Ranges of the alpha and Li-6 ions, for both branches
            B10_object (B10): Object to calculate interaction cross-sections
            al_sub (int): Aluminum substrate thickness in um
            coatings (np.array): Array containing blade coating thicknesses
            inclination (int): Incident neutron angle on the blades, 90 degrees
                               is for neutrons hitting perpendicularly.
        Returns:
            efficiency_array (np.array): Efficiency for the configuration
    """
    efficiency_list = []
    for wavelength in wavelengths:
        efficiency_at_wavelength = get_efficiency(wavelength, ranges, B10_object,
                                                  al_sub, coatings, inclination)
        efficiency_list.append(efficiency_at_wavelength)
    efficiency_array = np.array(efficiency_list)
    return efficiency_array

def get_efficiency_vs_lambda_no_single_blade(wavelengths, ranges, B10_object,
                                             al_sub, coatings, inclination):
    """ Calculates the efficiency vs lambda for a specific configuration of
        blades, where the coating on the first blade is missing.

        Args:
            wavelengths (np.array): Wavelengths in unit angstrom
            ranges (list): Ranges of the alpha and Li-6 ions, for both branches
            B10_object (B10): Object to calculate interaction cross-sections
            al_sub (int): Aluminum substrate thickness in um
            coatings (np.array): Array containing blade coating thicknesses
            inclination (int): Incident neutron angle on the blades, 90 degrees
                               is for neutrons hitting perpendicularly.
        Returns:
            efficiency_array (np.array): Efficiency for the configuration
    """
    efficiency_list = []
    for wavelength in wavelengths:
        efficiency_at_wavelength = get_efficiency_no_single_blade(wavelength, ranges,
                                                                  B10_object, al_sub,
                                                                  coatings, inclination)
        efficiency_list.append(efficiency_at_wavelength)
    efficiency_array = np.array(efficiency_list)
    return efficiency_array


def get_efficiency_only_double_coating(wavelengths, ranges, B10_object, al_sub,
                                       coatings, inclination):
    """ Calculates the efficiency for a specific configuration of
        blades, assuming only double-coated blades.

        Args:
            wavelengths (np.array): Wavelengths in unit angstrom
            ranges (list): Ranges of the alpha and Li-6 ions, for both branches
            B10_object (B10): Object to calculate interaction cross-sections
            al_sub (int): Aluminum substrate thickness in um
            coatings (np.array): Array containing blade coating thicknesses
            inclination (int): Incident neutron angle on the blades, 90 degrees
                               is for neutrons hitting perpendicularly.
        Returns:
            efficiency (np.array): Efficiency for the configuration
    """
    efficiency = []
    for wavelength in wavelengths:
        # Effect of aluminum
        varargin = Aluminium.aluminium(al_sub, [[wavelength]], inclination)[0]
        # Get sigma
        cross_section = B10_object.read_cross_section([[wavelength]])
        macro_cross_section = B10_object.macro_sigma(cross_section)
        sigma = B10_object.sigma_eq(macro_cross_section, inclination)[0]
        # Calculate efficiency
        __, eff_at_wavelength = efftools.mgeff_depth_profile(coatings, ranges,
                                                             sigma, varargin)
        efficiency.append(eff_at_wavelength)
    efficiency = np.array(efficiency)
    return efficiency

def get_average_efficiency(wavelengths, ranges, B10_object, al_sub,
                           coatings_vec, inclination):
    """ Calculates the average efficiency vs lambda for a specific configuration
        of blades, taking into consideration the thickness variation across
        the blades. Does this by scanning the blade configuration across
        the thickness variation (at n discrete data points) and calculating the
        average efficiency.

        Args:
            wavelengths (np.array): Wavelengths in unit angstrom
            ranges (list): Ranges of the alpha and Li-6 ions, for both decay
                           branches
            B10_object (B10): Object to calculate interaction cross-sections
            al_sub (int): Aluminum substrate thickness in um
            coatings_vec (np.array): Array containing blade coatings, where
                                     each element contains an array with
                                     the distribution of thicknesses along that
                                     blade.
            inclination (int): Incident neutron angle on the blades, 90 degrees
                               is for neutrons hitting perpendicularly.
        Returns:
            average_efficiency (np.array): Average efficiency across the blades.
    """
    number_data_points = len(coatings_vec[0])
    efficiencies = []
    for i in np.arange(0, number_data_points):
        # Get coatings
        coatings = []
        for vec in coatings_vec:
            coatings.append(vec[i])
        coatings = np.array(coatings)
        # Get efficiency
        efficiency = get_efficiency_vs_lambda(wavelengths, ranges, B10_object,
                                              al_sub, coatings, inclination)
        efficiencies.append(efficiency)
    # Get average efficiency
    average_efficiency = np.array(sum(efficiencies)/len(efficiencies))
    return average_efficiency


def get_triple_blade_thickness_distribution(x):
    """ Calculates the relative thickness, 0->1, at a position x along the
        triple blade. The position x is relative to the center.

        Args:
            x (np.array): Positions along the triple blade relative to the
                          center.
        Returns:
            y (np.array): Relative thickness at the positions x

    """
    # Declare equation parameters
    B0 = 0.99373
    B1 = 7.79E-04
    B2 = -3.86E-04
    B3 = -7.53E-06
    B4 = -9.62E-07
    B5 = 8.50E-09
    B6 = 3.71E-10
    # Get thickness y corresponding to trippel blade position x
    y = B0 + B1*x + B2*(x**2) + B3*(x**3) + B4*(x**4) + B5*(x**5) + B6*(x**6)
    return y

def meV_to_A(energy):
    """ Converts Energy in meV to wavelength in Angstrom. """
    return np.sqrt(81.81/energy)

def A_to_meV(wavelength):
    """ Converts wavelength in Angstrom to Energy in meV. """
    return (81.81 /(wavelength ** 2))

def get_absorption(B10_object, inclination, wavelengths, thickness_in_um):
    abs_prob_list = []
    for wavelength in wavelengths:
        sigma_eq = get_sigma_eq(wavelength, inclination, B10_object)
        abs_prob_list.append(1 - np.exp(-thickness_in_um*sigma_eq))
    abs_prob_np = np.array(abs_prob_list)
    return abs_prob_np
