# -*- coding: utf-8 -*-
#
# This file is part of MIEZE simulation.
# Copyright (C) 2019, 2020 TUM FRM2 E21 Research Group.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""General beamline class implementation."""

from copy import deepcopy
import numpy as np
import os
import random

from simulation.particles.neutron import Neutron

from utils.helper_functions import get_phi, find_nearest, load_obj, rotate

from simulation.beamline.beamline_properties import angular_distribution_in_radians, speed_std


cwd = os.getcwd()


class NeutronBeam:
    """Implements neutrons and its properties."""

    gamma = 1.83247172e4

    def __init__(self, beamsize, speed, total_simulation_time):

        self.beamsize = beamsize
        self.speed = speed
        self.total_simulation_time = total_simulation_time

        self.neutrons = []
        self.number_of_neutrons = None

        self.polarisation = dict()

        self.b_map = None

        self.x_range = None
        self.y_range = None
        self.z_range = None

        self.x_start = None
        self.x_end = None

        self.x_step = None

        self.y_start = None
        self.y_end = None

        self.z_start = None
        self.z_end = None

        self.t_step = None
        self.t_end = None

    def initialize_computational_space(self, **kwargs):
        """Initialize the 3d discretized computational space.

        It should be identical (or at least similar) to the computed magnetic field values.
        """
        self.x_start = kwargs.pop('x_start', 0)
        self.x_end = kwargs.pop('x_end', 1)
        self.x_step = kwargs.pop('x_step', 0.1)

        self.y_start = kwargs.pop('y_start', 0)
        self.y_end = kwargs.pop('y_end', 1)
        self.z_start = kwargs.pop('z_start', 0)
        self.z_end = kwargs.pop('z_end', 1)

        yz_step = kwargs.pop('yz_step', 0.1)

        self.x_range = np.arange(self.x_start, self.x_end + self.x_step, self.x_step)
        self.y_range = np.arange(self.y_start, self.y_end + yz_step, yz_step)
        self.z_range = np.arange(self.z_start, self.z_end + yz_step, yz_step)

    def initialize_time_evolution_space(self):
        """Set the time variables."""
        self.t_step = self.x_step / self.speed

    def create_neutrons(self, distribution, number_of_neutrons, polarisation, starting_position_x=0.):

        """Initialize the neutrons with a specific distribution.

        Parameters
        ----------
        distribution: boolean, optional
            # ToDo: Requires more testing!
            If True, then the neutrons are uniformly distributed.
            If False, then the neutrons are not spread and all start at 0.
        number_of_neutrons: int
            Number of neutrons to be simulated.
        polarisation: np.array
            The initial polarisation of neutrons.
        starting_position_x: float, optional
            The starting position for the neutrons along the beamline.
            Defaults to 0.
        """
        created_neutrons = 0
        while created_neutrons < number_of_neutrons:
            if distribution:

                # ToDo:
                # Make sure tha the magnetic field is computed at the computational grid required point.
                pos_y = random.gauss(0, self.beamsize / 5)
                pos_z = random.gauss(0, self.beamsize / 5)

                # ToDo: cut to less digits for the position
                # pos_y = round(random.gauss(0, self.beamsize / 5), ndigits=-int(np.log10(self.incrementsize)))
                # pos_z = round(random.gauss(0, self.beamsize / 5), ndigits=-int(np.log10(self.incrementsize)))

                # ToDo: Randomized velocities
                speed = random.gauss(self.speed, speed_std)

                # radial_speed = 0
                radial_speed = speed * random.gauss(0, np.tan(angular_distribution_in_radians))
                phi = get_phi(pos_y, pos_z)

                speed = random.gauss(self.speed, speed_std)

                # Todo: Implement radial velocity such that some neutrons are still within the beamline at th end

                neutron_velocity = np.array([speed,
                                             radial_speed * np.cos(phi),
                                             radial_speed * np.sin(phi)])

            else:
                pos_y = 0.
                pos_z = 0.

                speed = self.speed
                # speed = random.gauss(self.speed, speed_std)

                neutron_velocity = np.array([speed, 0, 0])

            position = np.asarray([starting_position_x, pos_y, pos_z])

            neutron = Neutron(polarisation=polarisation, position=position, velocity=neutron_velocity)

            self.neutrons.append(neutron)

            created_neutrons += 1

    def _time_in_field(self, speed):
        """Compute the time spent in the field."""
        return self.x_step / speed

    def _omega(self, b):
        return b * self.gamma

    def _precession_angle(self, time_increment, magnetic_field_vector):
        """Compute the precession angle.

        Parameters
        ----------
        time_increment: float
            Time increment, corresponds the time the neutrons spent in the voxel of the magnetic field.
        magnetic_field_vector: ndarray
            Magnetic field vector.

        Returns
        -------

        """
        return self.gamma * np.linalg.norm(magnetic_field_vector) * time_increment

    def _polarisation_change(self, neutron, magnetic_field_vector, time_increment):
        """Change the polarisation for the respective neutron.

        Parameters
        ----------
        neutron:
            Instance of Neutron class
        magnetic_field_vector: np.array
            Array of the magnetic field.

        Returns
        -------

        """
        phi = self._precession_angle(time_increment, magnetic_field_vector)
        return rotate(vector=neutron.polarisation, phi=phi, axis=magnetic_field_vector)

    def compute_beam(self):
        """Compute the polarisation of the beam along the trajectory."""

        for neutron in self.neutrons:

            self.check_neutron_in_beam(neutron)

            time_increment = self._time_in_field(speed=neutron.speed)

            neutron.update_position(time_increment)
            neutron.update_position_yz(time_increment)

            magnetic_field_value = self.get_magnetic_field(neutron.position)
            neutron.polarisation = self._polarisation_change(neutron, magnetic_field_value, time_increment)

            neutron.trajectory.append(neutron.position)

            # print(f'Magnetic field felt by neutron: {magnetic_field_value} at position {neutron.position}')

    def compute_average_polarisation(self):
        """Compute the polarisation for the entire experimental_setup."""
        neutron_list = deepcopy(self.neutrons)

        for position_x in self.x_range:

            neutrons_in_cell = 0

            for neutron in neutron_list:
                # Check whether the neutron is in the cell, defined from the left edge
                if position_x < neutron.position[0] < position_x + self.x_step:
                    if neutrons_in_cell == 0:
                        self.polarisation[position_x, 0, 0] = neutron.polarisation
                    else:
                        self.polarisation[position_x, 0, 0] += neutron.polarisation

                    neutrons_in_cell += 1

                    # Do this to increase computational speed
                    neutron_list.remove(neutron)

            # Compute the polarisation only if at least one neutron is in the respective cell.
            if neutrons_in_cell:
                # print(f'neutrons in cell: {neutrons_in_cell}')
                self.polarisation[position_x, 0, 0] /= neutrons_in_cell

    def get_magnetic_field(self, neutron_position):
        """Return the magnetic field at the specified position and time instance.

        Parameters
        ----------
        neutron_position: ndarray

        Returns
        -------
        out: ndarray
        """
        magnetic_field = self.get_magnetic_field_value_at_neutron_position(neutron_position)
        return magnetic_field

    def load_magnetic_field(self, data_file_at_time_instance=f'../../data/data_magnetic_field', b_map=None):
        """Load the magnetic field data."""
        # print(b_map)
        if b_map:
            self.b_map = b_map
        elif data_file_at_time_instance:
            self.b_map = load_obj(data_file_at_time_instance)

    def get_magnetic_field_value_at_neutron_position(self, neutron_position):
        """Returns the magnetic field at the location of the magnetic field.

        Handles the case when the magnetic field does not contain a value at the required point.
        """
        try:
            # print(f'Total magnetic field: {self.b_map}')
            return self.b_map[(find_nearest(self.x_range, neutron_position[0], index=False),
                               find_nearest(self.y_range, neutron_position[1], index=False),
                               find_nearest(self.z_range, neutron_position[2], index=False))]
        except KeyError:
            raise Exception(f'Could not find the magnetic field at the neutron position: {neutron_position}\n'
                            f'It is most probable that the magnetic field needs to be reevaluated.')

    def check_neutron_in_beam(self, neutron):
        """Check if neutron is in the calculated beam profile (y,z plane)"""
        x_condition = self.x_start <= neutron.position[0] <= self.x_end
        y_condition = self.y_start <= neutron.position[1] <= self.y_end
        z_condition = self.z_start <= neutron.position[2] <= self.z_end
        if not y_condition or not z_condition:
            print("Removed neutron because it diverged outside the beam along y or z.")
            self.neutrons.remove(neutron)
        elif not x_condition:
            print("Removed neutron because it reached the end outside beamline direction.")
            self.neutrons.remove(neutron)

    def get_pol(self):
        """Get the average polarisation for the beam."""
        # print([neutron.polarisation for neutron in self.neutrons])
        pol_x, pol_y, pol_z = 0, 0, 0
        n = len(self.neutrons)
        for neutron in self.neutrons:
            pol_x += neutron.polarisation[0]
            pol_y += neutron.polarisation[1]
            pol_z += neutron.polarisation[2]
        pol_x /= n
        pol_y /= n
        pol_z /= n

        # ToDo: compare which method is more computationally efficient
        # pol_x = np.average([neutron.polarisation[0] for neutron in self.neutrons])
        # pol_y = np.average([neutron.polarisation[1] for neutron in self.neutrons])
        # pol_z = np.average([neutron.polarisation[2] for neutron in self.neutrons])

        return pol_x, pol_y, pol_z

    def reset_pol(self):
        """Reset the polarisation for each neutron to the initial polarisation."""
        for neutron in self.neutrons:
            neutron.reset_pol()

    def get_neutron_position(self, index=0):
        """Return the position of the neutron at index in the neutron list."""
        return self.neutrons[index].position

    def collimate_neutrons(self, max_angle):
        """Apply a cut on the neutrons based on their angular distribution."""
        for neutron in self.neutrons:
            radial_speed = neutron.velocity[1] + neutron.velocity[2]
            angle = np.arctan(radial_speed/neutron.velocity[0])

            if angle > max_angle:
                self.neutrons.remove(neutron)

    def monochromate_neutrons(self, wavelength_min, wavelength_max):
        """Apply a cut on the neutrons based on their wavelength/speed distribution."""
        for neutron in self.neutrons:
            if neutron.wavelength > wavelength_max or neutron.wavelength < wavelength_min:
                self.neutrons.remove(neutron)
