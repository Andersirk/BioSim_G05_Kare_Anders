# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import unittest
import src.biosim.animals as ani
import pytest
import src.biosim.cell_topography as topo


# Birth weight


class AnimalsTest(unittest.TestCase):
    def test_birthweight_sd0(self):
        # Test that the birth weight is correct
        ani.Herbivores.parameters["w_birth"] = 10
        ani.Herbivores.parameters["sigma_birth"] = 0
        self.assertAlmostEqual(ani.Herbivores.birth_weight(ani.Herbivores()), 10)

# Fitness


def test_fitness_level_is_zero_when_weight_is_zero():
    herbivore = ani.Herbivores()
    herbivore.weight = 0
    assert herbivore.fitness == 0


def test_fitness_level_is_between_zero_and_one():
    herbivore = ani.Herbivores()
    herbivore.weight = 100
    herbivore.age = 0
    assert herbivore.fitness >= 0
    assert herbivore.fitness <= 1

# Natural death


@pytest.fixture
def strong_vs_weak():
    cell = topo.Desert()
    herbivore = ani.Herbivores()
    carnivore = ani.Carnivores()
    herbivore.weight, herbivore.age = 1, 100
    carnivore.weight, carnivore.age = 15, 52
    cell.add_animal(herbivore)
    cell.add_animal(carnivore)
    return herbivore, carnivore, cell


def test_natural_death(strong_vs_weak):
    """
    Expected probability for natural_death = omega(1-fitness).
    This test tests that an very unfit herbivore natural death prop =
    0.4(1-0) ≃ 0.4. and a very fit carnivore natural death prop =
    0.9(1-0.95) ≃ 0.045
    """
    die_rate_herbivore = [strong_vs_weak[0].will_die_natural_death() for _ in range(1000)]
    herbivore_amount = die_rate_herbivore.count(True)
    die_rate_carnivore = [strong_vs_weak[1].will_die_natural_death() for _ in range(1000)]
    carnivore_amount = die_rate_carnivore.count(True)
    assert 350 < herbivore_amount < 450
    assert 30 < carnivore_amount < 60


# carnivore kills herbivore


def test_fit_carnivore_kills_unfit_herbivore(strong_vs_weak):
    """
    A carnivore can only kill a certain amount of herbivores per year,
    limited by the parameter "F", which by default is 50. This means that the
    carnivore only can kill 50 1 kg herbivores. It will then have gained
    50(amount)*1 kg*0.75(beta) kg.
    """
    assert strong_vs_weak[1].eaten_this_year == 0
    n = 1000
    kill_rate = [strong_vs_weak[1].kills_herbivore(strong_vs_weak[0]) for _ in range(n)]
    amount = kill_rate.count(True)
    assert amount == 50
    assert strong_vs_weak[1].eaten_this_year == 50
    assert strong_vs_weak[1].weight == 15 + (amount*1*0.75)
    # Resets the amount_eaten_this_year to 0, and check if the carnivore's
    # eaten_this_year == 0 and that the weight not are effected by this.
    strong_vs_weak[1].reset_amount_eaten_this_year()
    assert strong_vs_weak[1].eaten_this_year == 0
    assert strong_vs_weak[1].weight == 15 + (amount*1*0.75)
    # Test when carnivore.fitness - herbivore.fitness) >
    # self.parameters["DeltaPhiMax"]
    strong_vs_weak[1].weight = 10
    strong_vs_weak[1].parameters["DeltaPhiMax"] = 0.0
    strong_vs_weak[1].kills_herbivore(strong_vs_weak[0])
    assert strong_vs_weak[1].weight == 10 + 0.75



# Set parameters


@pytest.mark.parametrize("bad_parameters", [{"w_birth": -6.0},
    {"sigma_birth": -1.0},
    {"beta": -0.75},
    {"eta": 2},
    {"a_half": -60.0},
    {"phi_age": -0.3},
    {"w_half": -4},
    {"phi_weight": -0.4},
    {"mu": -0.4},
    {"lambda": -1.0},
    {"gamma": -0.8},
    {"zeta": -3.5},
    {"xi": -1.1},
    {"omega": -0.9},
    {"F": -50},
    {"DeltaPhiMax": 0},
    {"not_a_para": 0.5}])
def test_set_parameters(bad_parameters):
    """Test if the non allowed parameters raises a value error. """
    carnivore = ani.Carnivores()
    herbivore = ani.Herbivores()
    with pytest.raises(ValueError):
        carnivore.set_parameters(bad_parameters)
    with pytest.raises(ValueError):
        herbivore.set_parameters(bad_parameters)
    carnivore.set_parameters({"w_birth": 6.0})
    assert carnivore.parameters["w_birth"] == 6.0


# Herbivore grazing


def test_herbivore_grazing():
    herbivore = ani.Herbivores()
    pre_eating_weight = herbivore.weight
    desert_cell = topo.Desert()
    herbivore.graze(desert_cell)
    assert herbivore.weight == pre_eating_weight
    jungle_cell = topo.Jungle()
    herbivore.graze(jungle_cell)
    assert herbivore.weight == pre_eating_weight + (
            herbivore.parameters["beta"]*herbivore.parameters["F"])
    after_jungle_graze = herbivore.weight
    savanna_cell = topo.Savanna()
    herbivore.graze(savanna_cell)
    assert herbivore.weight == after_jungle_graze + (
            herbivore.parameters["beta"]*herbivore.parameters["F"])

# Breeding


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

# Annual weight decrease, age up


def test_annual_weight_decrease_age_up():
    herbivore = ani.Herbivores()
    pre_decrease_weight = herbivore.weight
    herbivore.annual_weight_decrease()
    herbivore.age_up()
    assert herbivore.weight == pre_decrease_weight - (herbivore.parameters["eta"] * pre_decrease_weight)
    assert herbivore.age == 1
