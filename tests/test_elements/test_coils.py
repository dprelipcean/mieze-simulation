# -*- coding: utf-8 -*-
#
# This file is part of MIEZE simulation.
# Copyright (C) 2019, 2020 TUM FRM2 E21 Research Group.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Numerical tests for the codebase."""

from numpy import sqrt, pi
from unittest import TestCase

from simulation.elements.coils import Coil, RealCoil, RectangularCoil

from utils.physics_constants import MU_0


class TestRectangularCoil(TestCase):

    def setUp(self) -> None:
        self.coil = RectangularCoil(name='TestRectangularCoil', position=(0, 0, 0), length=1, windings=1, wire_d=1, current=1, width=1, height=1)

    def test_square_coil_center_value(self):
        """Test for a reference value in the center of a square coil."""

        # parameters
        current = 1
        side_length = 1

        conversion_factor = 10000
        reference_value = sqrt(2) * MU_0 * current / (pi * side_length) * conversion_factor

        numerical_error_acceptance = 1e-4

        self.coil.current = current

        # Evaluate
        test_value = self.coil.b_field([0, 0, 0])

        # print(f'{test_value} {reference_value}')

        # Assert
        assert abs(reference_value - test_value[2]) < numerical_error_acceptance
        self.assertEqual(test_value[1], 0)
        self.assertEqual(test_value[0], 0)


class TestSimpleCoil(TestCase):

    def setUp(self) -> None:
        self.coil = Coil(name='TestCoil', position=(0, 0, 0), length=1, r_eff=1, current=1, windings=1, wire_d=0)

    def test_circular_simple_coil_center_value(self):
        # parameters
        parameter_space = ((1, 1, 1, 1, 0), )

        for current, radius, windings, length, wire_d in parameter_space:
            self.coil.current = current
            self.coil.radius = radius
            self.coil.windings = windings
            self.coil.length = length
            self.coil.wire_d = wire_d

            # Setup
            conversion_factor = 10000
            reference_value = MU_0 * current * windings / sqrt((2 * radius) ** 2 + length ** 2) * conversion_factor

            numerical_error_acceptance = 1e-8

            # Evaluate
            test_value = self.coil.b_field([0, 0, 0])

            # print(f'{test_value} {reference_value}')

            # Assert
            assert abs(reference_value - test_value[0]) < numerical_error_acceptance
            self.assertEqual(test_value[1], 0)
            self.assertEqual(test_value[2], 0)


class TestRealCoil(TestCase):

    def setUp(self) -> None:
        self.coil = RealCoil(name='TestCoil', position=(0, 0, 0), length=1, r=1, current=1, windings=1, wire_d=1,
                             r_eff=1)

    def test_circular_real_coil_center_value(self):
        # parameters
        parameter_space = ((1, 1, 1, 1, 1), )

        for current, radius, windings, length, wire_d in parameter_space:
            self.coil.current = current
            self.coil.radius = radius
            self.coil.windings = windings
            self.coil.length = length
            self.coil.wire_d = wire_d

            # Setup
            conversion_factor = 10000
            reference_value = MU_0 * current * windings / sqrt((2 * radius) ** 2 + length ** 2) * conversion_factor

            numerical_error_acceptance = 1e-8

            # Evaluate
            test_value = self.coil.b_field([0, 0, 0])

            # print(f'{test_value} {reference_value}')

            # Assert
            assert abs(reference_value - test_value[0]) < numerical_error_acceptance
            self.assertEqual(test_value[1], 0)
            self.assertEqual(test_value[2], 0)
