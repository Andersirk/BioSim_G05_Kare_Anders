# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import src.biosim.cell_topography as topo
import pytest
import src.biosim.animals as animals
import src.biosim.Island as isle


@pytest.fixture
def basic_topography():
    return topo.Topography()

@pytest.mark.parametrize("fodder, requested, dec_amunt, fodder_result",
                         [(400, 200, 200, 200),
                          (100, 200, 100, 0),
                          (0, 200, 0, 0 )])

def test_Topo_decrease_fodder_abundance(basic_topography, fodder, requested, dec_amunt, fodder_result):
    """Tests that the amount of fodder can be decreased"""
    basic_topography.fodder = fodder
    decrease_amount = basic_topography.allowed_fodder_to_consume(requested)
    assert decrease_amount == dec_amunt
    assert basic_topography.current_fodder() == fodder_result


def test_Topo_current_occupants_int():
    """Test that the numbers of herbivore and carnivores occupants in a cell is an int"""
    instance = topo.Topography()
    assert type(instance.current_occupants()["Herbivores"]) == int and type(instance.current_occupants()["Carnivores"]) == int


def test_Topo_current_occupants_positive():
    """Test that the numbers of herbivore and carnivores occupants in a cell is either 0 or positive"""
    instance = topo.Topography()
    assert instance.current_occupants()["Herbivores"] >= 0 and instance.current_occupants()["Carnivores"] >= 0


def test_Topo_current_fodder():
    """Test that the amount of fodder is a float and greater than 0"""
    instance = topo.Topography()
    assert type(instance.current_fodder()) == float and instance.current_fodder() >= 0


def test_Topo_remove_herbivore():
    """Tests that an emigranting animal can be removed from its old cells animal list"""
    cell = topo.Topography()
    testherbi = animals.Herbivores()
    testlist = [animals.Herbivores() for _ in range(10)]
    cell.herbivore_list = testlist
    cell.add_animal(testherbi)
    cell.remove_animal(testherbi)
    assert testherbi not in cell.herbivore_list


def test_Topo_add_herbviore():
    """Tests that an imigranting animal can be added to the new cells animal list"""
    instance = topo.Topography()
    instance.add_animal(animals.Herbivores())
    assert len(instance.herbivore_list) == 1


def test_desert_fodder():
    """Tests that the desert dont have any fooder"""
    instance = topo.Desert()
    assert instance.current_fodder() == 0


def test_Mountain_fodder():
    """Tests that the mountains dont have any fooder"""
    instance = topo.Mountain()
    assert instance.is_accessible == False


def test_Ocean_fodder():
    """Tests that the oceans dont have any fooder"""
    instance = topo.Ocean()
    assert instance.is_accessible == False


@pytest.fixture
def low_fitness_animals():
    jungle_cell = topo.Desert()
    herbivore = animals.Herbivores()
    carnivore = animals.Carnivores()
    carnivore.weight, carnivore.age = 1, 1000
    herbivore.weight, herbivore.age = 1, 1000
    herbivore.parameters["omega"] = 1
    carnivore.parameters["omega"] = 1
    jungle_cell.add_animal(herbivore)
    jungle_cell.add_animal(carnivore)
    return jungle_cell


#migration
@pytest.fixture
def surrounding_ocean_cell():
    geogr = """\
                OOOOOOOOOOOOOOOOOOOOO
                OOOOOOOOSMMMMJJJJJJJO
                OSSSSSJJJJMMJJJJJJJOO
                OSSSSSSSSSMMJJJJJJOOO
                OSSSSSJJJJJJJJJJJJOOO
                OSSSSSJJJDDJJJSJJJOOO
                OSSJJJJJDDDJJJSSSSOOO
                OOSSSSJJJDDJJJSOOOOOO
                OSSSJJJJJDDJJJJJJJOOO
                OSSSSJJJJDDJJJJOOOOOO
                OOSSSSJJJJJJJJOOOOOOO
                OOOSSSSJJJJJJJOOOOOOO
                OOOOOOOOOOOOOOOOOOOOO"""
    island = isle.Island(geogr)
    occupants = [{'loc': (1, 19),
           'pop': [{'species': 'Herbivore',
               'age': 10, 'weight': 12.5},
              {'species': 'Herbivore',
               'age': 9, 'weight': 10.3}]}]
    island.populate_island(occupants)
    return island
def test_natural_death_in_all_cells(low_fitness_animals):
    low_fitness_animals.natural_death_all_animals_in_cell()
    assert len(low_fitness_animals.herbivore_list) == 0

def test_migrate_all_herb_in_cell_mock_ek():
    pass
