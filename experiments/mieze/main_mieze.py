# -*- coding: utf-8 -*-
#
# This file is part of MIEZE simulation.
# Copyright (C) 2019, 2020 TUM FRM2 E21 Research Group.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""An implementation of the MIEZE experimental_setup."""

from simulation.experimental_setup.setup import Setup

from experiments.mieze.parameters import (
    CONSIDER_EARTH_FIELD, COIL_SET_PARAMETERS, ELEMENTS_POSITIONS_ABSOLUTE, ELEMENTS_POSITIONS_RELATIVE,
    HELMHOLTZCOILS_PARAMETERS, SPIN_FLIPPER_PARAMETERS
)
from simulation.parameters_simulation import default_beam_grid

from simulation.elements.coils import Coil
from simulation.elements.coil_set import CoilSet
from simulation.elements.helmholtz_pair import HelmholtzPair
from simulation.elements.polariser import Polariser
from simulation.elements.spin_flipper import SpinFlipper


class Mieze(Setup):
    """Implementation of the MIEZE experimental_setup at FRM2."""

    def __init__(self, coil_type=Coil, **kwargs):

        consider_earth_field = kwargs.get('consider_earth_field', CONSIDER_EARTH_FIELD)
        save_individual_data_sets = kwargs.get('save_individual_data_sets', False)

        super(Mieze, self).__init__(consider_earth_field, save_individual_data_sets)

        self.spin_flipper_distance = kwargs.get('spin_flipper_distance')
        self.coil_set_distance = kwargs.get('coil_set_distance')

        self.coil_type = coil_type

    def create_setup(self):
        """Create the elements for the experimental_setup."""

        self.create_element(element_class=Polariser,
                            position=(ELEMENTS_POSITIONS_ABSOLUTE["polariser"], 0, 0))

        self.create_element(coil_type=Coil,
                            current=HELMHOLTZCOILS_PARAMETERS["current"],
                            element_class=HelmholtzPair,
                            position=(HELMHOLTZCOILS_PARAMETERS["position"], 0, 0),
                            radius=HELMHOLTZCOILS_PARAMETERS["radius"])

        self.create_element(element_class=SpinFlipper,
                            **SPIN_FLIPPER_PARAMETERS)

        self.create_element(element_class=CoilSet,
                            current=COIL_SET_PARAMETERS["current"],  # [A]
                            name='CoilSet',
                            position=COIL_SET_PARAMETERS['position'] + self.coil_set_distance)

        self.update_metadata()


def compute_magnetic_field_mieze(grid_size=default_beam_grid,
                                 coil_set_distance=ELEMENTS_POSITIONS_RELATIVE["coil_set_distance"],
                                 spin_flipper_distance=ELEMENTS_POSITIONS_RELATIVE["spin_flipper_distance"],
                                 filename='data/data_magnetic_field',
                                 save_individual_data_sets=True):
    """Compute the magnetic field for the MIEZE experimental_setup.

    Parameters
    ----------
    grid_size: dict
        Parameters for the computational space grid in 3D.
    coil_set_distance: float
        Distance between the CoilSet and the Helmholtz Coils/Spin Flipper.
    spin_flipper_distance: float
        Distance between the Polariser and the Spin Flipper.
    filename: str
        The filename to store the magnetic field data to.
    save_individual_data_sets: bool
        Flag indicating whether to store the magnetic field from the individual components as well.
    """

    # Initialize an object from the MIEZE class
    experiment = Mieze(spin_flipper_distance=spin_flipper_distance,
                       coil_set_distance=coil_set_distance,
                       save_individual_data_sets=save_individual_data_sets)

    # Create the components of the beamline with their parameters
    experiment.create_setup()

    # Initialize the computational space (grid) and compute the magnetic field for it
    experiment.initialize_computational_space(**grid_size)
    experiment.calculate_static_b_field()

    # Compute the magnetic field for one point only
    # output = experiment.calculate_b_field(point=(0, 0, 0))
    # print(output)

    # Save the obtained data to a file
    experiment.save_total_data_to_file(filename=filename)

    # Plot results
    # experiment.set_plot_ticks(set_ticks=False)

    # experiment.plot_field_1d_scalar(component='x')
    # experiment.plot_field_1d_scalar(component='y')
    # experiment.plot_field_1d_scalar(component='z')


if __name__ == '__main__':
    # Use this filename by default.
    # filename = './../../../data/data_magnetic_field'

    # Use this to investigat the polarisation
    filename = '../../../analysises/adiabatic_polarisation/data/data_magnetic_field_mieze'

    compute_magnetic_field_mieze(filename=filename)
