# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import unittest
import src.biosim.animals as ani
import pytest
import random


class AnimalsTest(unittest.TestCase):
    def test_birthweight_sd0(self):
        # Test that the birth weight is correct
        ani.Herbivores.parameters["w_birth"] = 10
        ani.Herbivores.parameters["sigma_birth"] = 0
        self.assertAlmostEqual(ani.Herbivores.birth_weight(ani.Herbivores()), 10)


@pytest.fixture
def herbivore_zero_weight():
    instance = ani.Herbivores()
    instance.weight = 0
    return instance


def test_fitnesslevel_is_zero_when_weight_is_zero(herbivore_zero_weight):
    assert herbivore_zero_weight.fitness == 0

@pytest.fixture
def herbivore_great_age_and_weight():
    instance = ani.Herbivores()
    instance.weight = 80
    instance.age = 20
    return instance

def test_fitnesslevel_is_between_zero_and_one(herbivore_great_age_and_weight):
    assert herbivore_great_age_and_weight.fitness >= 0
    assert herbivore_great_age_and_weight.fitness <= 1










