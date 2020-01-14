# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import unittest
import src.biosim.animals as ani
import src.biosim.cell_topography as topo
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


def test_breed_certain_probability():
    cell = topo.Jungle()
    herbivore = ani.Herbivores()
    herbivore.weight, herbivore.age = 80, 30
    cell.add_animal(herbivore)
    herbivore.breed(cell, 100)
    assert len(cell.herbivore_list) == 2
    assert isinstance(cell.herbivore_list[0], ani.Herbivores)
    assert isinstance(cell.herbivore_list[1], ani.Herbivores)

def test_breed_uncertain_probability():
    #about 0.4 probabilty for birth
    born=0
    for _ in range(1000):
        cell = topo.Jungle()
        herbivore = ani.Herbivores()
        herbivore.weight, herbivore.age = 400, 10
        cell.add_animal(herbivore)
        herbivore.breed(cell, 3)
        if len(cell.herbivore_list) == 2:
            born += 1
    assert born > 350
    assert born < 450

def test_breed_certain_probability_all_in_cell():
    cell = topo.Jungle()
    herbivore = ani.Herbivores()
    herbivore.weight, herbivore.age = 80, 30
    for _ in range(100):
        cell.add_animal(ani.Herbivores(age=10, weight=100))
    cell.breed_all_animals_in_cell()
    assert len(cell.herbivore_list) == 200








