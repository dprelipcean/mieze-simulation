# -*- coding: utf-8 -*-
#
# This file is part of MIEZE simulation.
# Copyright (C) 2019, 2020 TUM FRM2 E21 Research Group.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Parameters for the neutron beam simulatoin for the MIEZE setup."""

import numpy as np

# Variables are stored as tuples with numerical value and units
I_real_coil = 10  # [A]


# MIEZE coil set values

# Inner coils
LENGTH_COIL_INNER = 86 * 1e-3  # [m]
RADIUS_COIL_INNER_EFFECTIVE = 177 / 2. * 1e-3   # [m]
N_WINDINGS_COIL_INNER = 168   #

RADIUS_COIL_INNER_MIN = 50 * 1e-3  # [m]
RADIUS_COIL_INNER_MAX = 252.30 / 2 * 1e-3  # [m]

RADIAL_LAYERS = 13

# Outer Coils
LENGTH_COIL_OUTER = 50 * 1e-3   # [m]
RADIUS_COIL_OUTER_EFFECTIVE = 130 * 1e-3   # [m]
N_WINDINGS_COIL_OUTER = 48   #

RADIUS_COIL_OUTER_MIN = 220 / 2 * 1e-3  # [m]
RADIUS_COIL_OUTER_MAX = 301.80 / 2 * 1e-3  # [m]


DISTANCE_BETWEEN_INNER_COILS = 115 * 1e-3 - LENGTH_COIL_INNER  # [m]

DISTANCE_2ND_COIL = 73 * 1e-3   # [m]
DISTANCE_3RD_COIL = 187 * 1e-3   # [m]
DISTANCE_4TH_COIL = 260 * 1e-3   # [m]

WIRE_D = 5 * 1e-3  # [m]
WIRE_SPACING = 1 * 1e-3  # [m]
COIL_SET_CURRENT = 5  # [A]

WIDTH_CBOX = 2 * (LENGTH_COIL_OUTER + LENGTH_COIL_INNER) + DISTANCE_BETWEEN_INNER_COILS  # [m]

# Square coil Parameters
SQUARE_COIL_POSITION_1ST = 0.1   # [m]
SQUARE_COIL_POSITION_2ND = 1   # [m]

# Rectangular coils

# Coil group
L1 = 0.53   # [m]  # coil group A to B
L2 = 2.58   # [m]  # coil group B to detector
Ls = L2 - 0.62   # [m]  # sample to detector

# Spin flippers
R_HSF = 53.8 * 1e-3   # [m]  # radius of helmholtz coils at the spin flippers; achieved by fitting real magnetic field

# Polariser data
POLARISATOR = 0.0

# distance between polariser and first coil of hsf1
POLARISER_HSF1 = 0.45  # Value used for testing
# POLARISER_HSF1 = 0.125  # Real, experimental value
HelmholtzSpinFlipper_position_HSF1 = POLARISATOR + POLARISER_HSF1 + R_HSF / 2.0
SpinFlipper_position1 = HelmholtzSpinFlipper_position_HSF1

COIL_A = HelmholtzSpinFlipper_position_HSF1 + R_HSF / 2.0
COIL_B = COIL_A + L1

distance_between_HSF1_coilset = 0.0
CoilSet_position = SpinFlipper_position1 + R_HSF / 2.0 + WIDTH_CBOX/2


# Beam properties
beamsize = 0.02
number_of_neutrons = 1


# Neutron wavelength and speed properties
wavelength = 4.3  # [Angstrom]

wavelength_min = 3.5
wavelength_max = 6

neutron_speed = 3956 / wavelength
speed_min = 3956 / wavelength_max
speed_max = 3956 / wavelength_min
speed_std = (speed_max - speed_min) / 4


c = 0.31225  # sqrt(1-polarisierung²)
x = c * np.random.rand()
z = np.sqrt(c ** 2 - x ** 2)

initial_polarisation = np.array([x, 0.95, z])

BEAM_PROPERTIES = {
    'beamsize': beamsize,
    'number_of_neutrons': number_of_neutrons,
    'speed': neutron_speed
}


# Angular distribution
angular_distribution = 45  # minutes
angular_distribution_in_radians = angular_distribution * np.pi / (60 * 180)


COIL_SET_PARAMETERS = {
    "CURRENT": 100,  # [A]
}

HELMHOLTZCOILS_PARAMETERS = {
    "CURRENT": 1.6,  # [A],
    "position": HelmholtzSpinFlipper_position_HSF1,
    "RADIUS": R_HSF
}

SPIN_FLIPPER_PARAMETERS = {
    "current": 1.6,  # [A]
    "position": (SpinFlipper_position1, 0, 0),
    "length": 1 * 1e-2,   # [m]
    "width": 1 * 1e-2,  # [m]
    "height": 1 * 1e-3,  # [m]
    "windings": 1,
    "wire_d":  5 * 1e-3  # [m]
}

ELEMENTS_POSITIONS_RELATIVE = {
    "coil_set_distance": distance_between_HSF1_coilset,
    "spin_flipper_distance": HelmholtzSpinFlipper_position_HSF1,
    "polariser": POLARISATOR
}

ELEMENTS_POSITIONS_ABSOLUTE = {
    "coil_set": CoilSet_position,
    "spin_flipper": HelmholtzSpinFlipper_position_HSF1,
    "polariser": POLARISATOR
}

startpoint = 0.000  # [m]
# beamend = CoilSet_position + 0.05  # [m]
beamend = HelmholtzSpinFlipper_position_HSF1 + 0.25  # [m]

npoints = 200

absolute_x_position = np.linspace(startpoint, beamend, num=npoints)

step_x = (absolute_x_position[1] - absolute_x_position[0])

default_beam_grid = {'x_start': startpoint, 'x_end': beamend, 'x_step': step_x,
                     'y_start': -0.0, 'y_end': 0.0, 'z_start': -0.0, 'z_end': 0.0, 'yz_step': 0.1}

total_simulation_time = beamend / neutron_speed
