# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import src.biosim.cell_topography as topo
import pytest
import src.biosim.animals as animals
import src.biosim.Island as isle


@pytest.fixture
def basic_jungle():
    return topo.Jungle()

@pytest.mark.parametrize("fodder, requested, dec_amunt, fodder_result",
                         [(400, 200, 200, 200),
                          (100, 200, 100, 0),
                          (0, 200, 0, 0 )])

def test_Topo_decrease_fodder_abundance(basic_jungle, fodder, requested, dec_amunt, fodder_result):
    """Tests that the amount of fodder can be decreased"""
    basic_jungle.fodder = fodder
    decrease_amount = basic_jungle.allowed_fodder_to_consume(requested)
    assert decrease_amount == dec_amunt
    assert basic_jungle.current_fodder() == fodder_result


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
    """Tests that an emigrating animal can be removed from its old cells animal list"""
    cell = topo.Topography()
    testherbi = animals.Herbivores()
    testlist = [animals.Herbivores() for _ in range(10)]
    cell.herbivore_list = testlist
    cell.add_animal(testherbi)
    cell.remove_animal(testherbi)
    assert testherbi not in cell.herbivore_list

def test_Topo_remove_carnivore():
    """Tests that an emigrating animal can be removed from its old cells animal list"""
    cell = topo.Topography()
    testcarni = animals.Carnivores()
    testlist = [animals.Carnivores() for _ in range(10)]
    cell.herbivore_list = testlist
    cell.add_animal(testcarni)
    cell.remove_animal(testcarni)
    assert testcarni not in cell.herbivore_list


def test_Topo_add_herbviore():
    """Tests that an imigranting animal can be added to the new cells animal list"""
    instance = topo.Topography()
    instance.add_animal(animals.Herbivores())
    assert len(instance.herbivore_list) == 1

def test_Topo_add_carnivore():
    """Tests that an imigranting animal can be added to the new cells animal list"""
    instance = topo.Topography()
    instance.add_animal(animals.Carnivores())
    assert len(instance.carnivore_list) == 1


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
    jungle_cell = topo.Jungle()
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
def standard_map_ani_one_accesible():
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
               'age': 9, 'weight': 10},
              {'species': 'Herbivore',
               'age': 9, 'weight': 10},
              {'species': 'Carnivore',
               'age': 9, 'weight': 10},
              {'species': 'Carnivore',
               'age': 9, 'weight': 10}]}]
    island.populate_island(occupants)
    return island


def test_migrate_all_herbi_in_cell_new_location(
        standard_map_ani_one_accesible):
    animals.Herbivores.parameters["mu"] = 1000
    mock_ek = {(1,18):2}
    standard_map_ani_one_accesible.raster_model[(1, 19)].migrate_all_herbivores_in_cell(standard_map_ani_one_accesible, (1, 19), mock_ek)
    assert standard_map_ani_one_accesible.raster_model[(1, 19)].herbivore_list == []
    assert standard_map_ani_one_accesible.raster_model[(1, 18)].herbivore_list != []


def test_migrate_all_carni_in_cell_new_location(
        standard_map_ani_one_accesible):
    animals.Carnivores.parameters["mu"] = 1000
    mock_ek = {(1,18):2}
    standard_map_ani_one_accesible.raster_model[(1, 19)].migrate_all_carnivores_in_cell(standard_map_ani_one_accesible, (1, 19), mock_ek)
    assert standard_map_ani_one_accesible.raster_model[(1, 19)].carnivore_list == []
    assert standard_map_ani_one_accesible.raster_model[(1, 18)].carnivore_list != []

# breeding

def test_breed__certain_probability_all_in_cell():
    cell = topo.Jungle()
    for _ in range(100):
        cell.add_animal(animals.Herbivores(age=10, weight=100))
        cell.add_animal(animals.Carnivores(age=10, weight=100))
    cell.breed_all_animals_in_cell()
    assert len(cell.herbivore_list) == 200
    assert len(cell.carnivore_list) == 200

#cell ek

def test_ek_for_cell_9_herbs_carns_100_fodder(basic_jungle):
    basic_jungle.fodder = 100
    for _ in range(9):
        basic_jungle.add_animal(animals.Herbivores(weight=10))
        basic_jungle.add_animal(animals.Carnivores())
    ek_herbivores = basic_jungle.ek_for_cell("Herbivores")
    ek_carnivores = basic_jungle.ek_for_cell("Carnivores")
    assert ek_herbivores == 1
    assert ek_carnivores == 0.18






def test_natural_death_in_all_cells(low_fitness_animals):
    low_fitness_animals.natural_death_all_animals_in_cell()
    assert len(low_fitness_animals.herbivore_list) == 0
    assert len(low_fitness_animals.carnivore_list) == 0


def test_feeding():
    jungle_cell = topo.Jungle()
    [jungle_cell.add_animal(animals.Herbivores()) for herbivores in range(250)]
    [jungle_cell.add_animal(animals.Carnivores()) for carnivores in range(250)]
    herbivore_fitness_sort = sorted(jungle_cell.herbivore_list,
                                    key=lambda herbi: herbi.fitness, reverse=True)
    testani = herbivore_fitness_sort[0]
    least_fittest_weight = testani.weight
    jungle_cell.feed_herbivores_in_cell()
    assert least_fittest_weight == testani.weight





