# -*- coding: utf-8 -*-
#
# This file is part of MIEZE simulation.
# Copyright (C) 2019 TUM FRM2 E21 Research Group.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Neutron class."""

import itertools
from multiprocessing import Pool
import numpy as np
import numpy.random as r
import os
import random

from particles.neutron import Neutron

from utils.helper_functions import save_obj, load_obj, _find_nearest

cwd = os.getcwd()


class NeutronBeam:
    """Implements neutrons and its properties."""

    def __init__(self, beamsize, number_of_neutrons, incrementsize, velocity, totalflightlength):
        self.neutrons = []
        self.number_of_neutrons = number_of_neutrons
        self.velocity = velocity
        self.incrementsize = incrementsize
        self.totalflightlength = totalflightlength
        self.beamsize = beamsize

        self.polarisation = dict()

    def initialize_computational_space(self, **kwargs):
        """Initialize the 3d discretized computational space."""
        x_start = kwargs.pop('x_start', 0)
        x_end = kwargs.pop('x_end', 1)
        x_step = kwargs.pop('x_step', 0.1)

        y_start = kwargs.pop('y_start', 0)
        y_end = kwargs.pop('y_end', 1)
        z_start = kwargs.pop('z_start', 0)
        z_end = kwargs.pop('z_end', 1)
        yz_step = kwargs.pop('yz_step', 0.1)

        self.x_range = np.arange(x_start, x_end + x_step, x_step)
        self.y_range = np.arange(y_start, y_end + yz_step, yz_step)
        self.z_range = np.arange(z_start, z_end + yz_step, yz_step)

    def create_neutrons(self, distribution=False):
        """Initialize the neutrons."""
        while len(self.neutrons) < self.number_of_neutrons:
            c = 0.31225  # sqrt(1-polarisierung²)
            x = c * r.rand()
            z = np.sqrt(c ** 2 - x ** 2)

            speed = random.gauss(self.velocity, 0.02 * self.velocity)
            polarisation = np.array([x, 0.95, z])

            if distribution:
                pos_y = round(random.gauss(0, self.beamsize / 5), ndigits=-int(np.log10(self.incrementsize)))
                pos_z = round(random.gauss(0, self.beamsize / 5), ndigits=-int(np.log10(self.incrementsize)))
            else:
                pos_y = 0
                pos_z = 0
            position = (0, pos_y, pos_z)

            neutron = Neutron(polarisation=polarisation, position=position, speed=speed)

            self.neutrons.append(neutron)

    def _time_in_field(self, velocity):
        return self.incrementsize / velocity

    @staticmethod
    def _omega(b):
        gamma = 1.83247172e4
        return b * gamma

    @staticmethod
    def _precession_angle(time, b):
        gamma = 1.83247172e4
        return gamma * np.linalg.norm(b) * time

    @staticmethod
    def _rotate(vektor, phi, axis):
        n = axis / np.linalg.norm(axis)
        c = np.cos(phi)
        s = np.sin(phi)
        n1 = n[0]
        n2 = n[1]
        n3 = n[2]
        R = [[n1 ** 2 * (1 - c) + c, n1 * n2 * (1 - c) - n3 * s, n1 * n3 * (1 - c) + n2 * s],
             [n2 * n1 * (1 - c) + n3 * s, n2 ** 2 * (1 - c) + c, n2 * n3 * (1 - c) - n1 * s],
             [n3 * n1 * (1 - c) - n2 * s, n3 * n2 * (1 - c) + n1 * s, n3 ** 2 * (1 - c) + c]]
        return np.dot(R, vektor)

    def _polarisation_change(self, neutron, b, L):
        t = self._time_in_field(velocity=neutron.speed)
        phi = self._precession_angle(t, b)
        return self._rotate(vektor=neutron.polarisation, phi=phi, axis=b)

    # def create_b_map(self, b_function, profiledimension):
    #     """
    #
    #     Parameters
    #     ----------
    #     b_function
    #     profiledimension: tuple
    #
    #     Returns
    #     -------
    #
    #     """
    #     if not len(profiledimension) == 2:
    #         print('error: profile dimension has to be 2D ')
    #         return -1
    #
    #     max_y = profiledimension[0]
    #     max_z = profiledimension[1]
    #
    #     x = np.round(np.arange(0, self.totalflightlength, self.incrementsize),
    #                  decimals=-int(np.log10(self.incrementsize)))
    #     y = np.round(np.arange(-max_y, max_y + self.incrementsize, self.incrementsize),
    #                  decimals=-int(np.log10(self.incrementsize)))
    #     z = np.round(np.arange(-max_z, max_z + self.incrementsize, self.incrementsize),
    #                  decimals=-int(np.log10(self.incrementsize)))
    #
    #     args = list(itertools.product(x, y, z))
    #
    #     with Pool(4) as p:
    #         result = p.map(b_function, args)
    #
    #     bmap = dict(zip(args, result))
    #
    #     # self.B_map = bmap
    #     save_obj(bmap, 'B_map')

    def compute_beam(self):
        self.b_map = load_obj('../data/data')

        for neutron in self.neutrons:
            self.simulate_neutron_trajectory(neutron)

    def simulate_neutron_trajectory(self, neutron):
        toberemoved = []

        # # ToDo: refactor
        # # check if it is in the calculated beamprofile (y,z plane)
        # if not (0, neutron.position[1], neutron.position[2]) in b_map:
        #     toberemoved.append(neutron)
        #     continue

        for j in self.x_range:

            neutron.set_position_x(j)

            neutron.polarisation = self._polarisation_change(
                neutron,
                self.b_map[(_find_nearest(self.x_range, neutron.position[0], index=False),
                            _find_nearest(self.y_range, neutron.position[1], index=False),
                            _find_nearest(self.z_range, neutron.position[2], index=False),
                            )],
                self.incrementsize)

            self.polarisation[self.get_neutron_position()] = self.get_pol()
            print(self.get_pol())
            print(self.get_neutron_position())

        for neutron in toberemoved:
            self.neutrons.remove(neutron)

    def get_pol(self):

        xpol = np.average([neutron.polarisation[0] for neutron in self.neutrons])
        ypol = np.average([neutron.polarisation[1] for neutron in self.neutrons])
        zpol = np.average([neutron.polarisation[2] for neutron in self.neutrons])

        return xpol, ypol, zpol

    def reset_pol(self):
        c = 0.31225  # sqrt(1-polarisierung²)
        x = c * r.rand()
        z = np.sqrt(c ** 2 - x ** 2)
        for neutron in self.neutrons:
            neutron.polarisation = np.array([x, 0.95, z])

    def get_neutron_position(self, index=0):
        return self.neutrons[index].position