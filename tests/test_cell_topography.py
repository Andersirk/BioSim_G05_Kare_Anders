# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import biosim.cell_topography as topo
import pytest
import biosim.animals as animals
import biosim.Island as isle


@pytest.fixture
def basic_jungle():
    return topo.Jungle()


@pytest.mark.parametrize("fodder, requested, dec_amunt, fodder_result",
                         [(400, 200, 200, 200), (100, 200, 100, 0),
                          (0, 200, 0, 0)])
def test_topo_decrease_fodder_abundance(basic_jungle, fodder, requested,
                                        dec_amunt, fodder_result):
    """Tests that the amount of fodder can be decreased"""
    basic_jungle.fodder = fodder
    decrease_amount = basic_jungle.allowed_fodder_to_consume(requested)
    assert decrease_amount == dec_amunt
    assert basic_jungle.current_fodder() == fodder_result


def test_topo_current_occupants_int():
    """Test that the numbers of herbivore and carnivores occupants in a cell
     is an int"""
    instance = topo.Topography()
    assert type(instance.current_occupants()["Herbivores"]) == int and type(
        instance.current_occupants()["Carnivores"]) == int


def test_topo_current_occupants_positive():
    """Test that the numbers of herbivore and carnivores occupants in a cell
     is either 0 or positive"""
    instance = topo.Topography()
    assert instance.current_occupants()["Herbivores"] >= 0\
        and instance.current_occupants()["Carnivores"] >= 0


def test_topo_current_fodder():
    """Test that the amount of fodder is a float and greater than 0"""
    instance = topo.Topography()
    assert type(instance.current_fodder()) == float \
        and instance.current_fodder() >= 0


def test_topo_remove_herbivore():
    """Tests that an emigrating animal can be removed from its old cells
     animal list"""
    cell = topo.Topography()
    testherbi = animals.Herbivores()
    testlist = [animals.Herbivores() for _ in range(10)]
    cell.herbivore_list = testlist
    cell.add_animal(testherbi)
    cell.remove_animal(testherbi)
    assert testherbi not in cell.herbivore_list


def test_topo_remove_carnivore():
    """Tests that an emigrating animal can be removed from its old cells
     animal list"""
    cell = topo.Topography()
    testcarni = animals.Carnivores()
    testlist = [animals.Carnivores() for _ in range(10)]
    cell.herbivore_list = testlist
    cell.add_animal(testcarni)
    cell.remove_animal(testcarni)
    assert testcarni not in cell.herbivore_list


def test_topo_add_herbviore():
    """Tests that an immigrating animal can be added to the new cells
     animal list"""
    instance = topo.Topography()
    instance.add_animal(animals.Herbivores())
    assert len(instance.herbivore_list) == 1


def test_topo_add_carnivore():
    """Tests that an immigrating animal can be added to the new cells
     animal list"""
    instance = topo.Topography()
    instance.add_animal(animals.Carnivores())
    assert len(instance.carnivore_list) == 1


def test_desert_fodder():
    """Tests that the desert dont have any fodder"""
    instance = topo.Desert()
    assert instance.current_fodder() == 0


def test_mountain_ocean_is_not_accessible():
    """Tests that the mountains dont have any fodder"""
    mountain = topo.Mountain()
    ocean = topo.Ocean()
    assert mountain.is_accessible is False
    assert ocean.is_accessible is False


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


def test_animal_with_fitness_level_0_dies():
    animal = animals.Herbivores(age=200, weight=1)
    cell = topo.Jungle()
    cell.add_animal(animal)
    animals.Herbivores.parameters["omega"] = 1
    cell.natural_death_all_animals_in_cell()
    animals.Herbivores.parameters["omega"] = 0.4
    assert len(cell.herbivore_list) == 0


# migration
@pytest.fixture
def standard_map_peninsula():
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
                  'pop': [{'species': 'Herbivore', 'age': 9, 'weight': 10},
                          {'species': 'Carnivore', 'age': 9, 'weight': 10}]}]
    island.populate_island(occupants)
    return island


def test_migrate_all_herbi_in_cell_new_location(
        standard_map_peninsula):
    """Tests that all herbivores in one cell moves to another cell when the
    migration-prop = 1"""
    animals.Herbivores.parameters["mu"] = 1000
    mock_ek = {(1, 18): 2}
    standard_map_peninsula.raster_model[(
        1, 19)]._migrate_all_herbivores_in_cell(
        standard_map_peninsula, (1, 19), mock_ek)
    animals.Herbivores.parameters["mu"] = 0.25
    assert standard_map_peninsula.raster_model[(1, 19)].herbivore_list == []
    assert standard_map_peninsula.raster_model[(1, 18)].herbivore_list != []


def test_migrate_all_carni_in_cell_new_location(
        standard_map_peninsula):
    """Tests that all carnivores in one cell moves to another cell when the
    migration-probability = 1"""
    animals.Carnivores.parameters["mu"] = 1000
    mock_ek = {(1, 18): 2}
    standard_map_peninsula.raster_model[(
        1, 19)]._migrate_all_carnivores_in_cell(
        standard_map_peninsula, (1, 19), mock_ek)
    animals.Carnivores.parameters["mu"] = 0.24
    assert standard_map_peninsula.raster_model[(1, 19)].carnivore_list == []
    assert standard_map_peninsula.raster_model[(1, 18)].carnivore_list != []


# breeding


def test_breed_certain_probability_all_in_cell():
    """Tests that all animals breed, when the breeding-probability = 1"""
    cell = topo.Jungle()
    for _ in range(100):
        cell.add_animal(animals.Herbivores(age=10, weight=100))
        cell.add_animal(animals.Carnivores(age=10, weight=100))
    cell.breed_all_animals_in_cell()
    assert len(cell.herbivore_list) == 200
    assert len(cell.carnivore_list) == 200


# cell ek


def test_ek_for_cell_9_herbs_carns_100_fodder(basic_jungle):
    """Tests that the ek formula for herbivores and carnivores are correct"""
    basic_jungle.fodder = 100
    for _ in range(9):
        basic_jungle.add_animal(animals.Herbivores(weight=10))
        basic_jungle.add_animal(animals.Carnivores())
    animals.Carnivores.parameters["F"] = 50
    ek_herbivores = basic_jungle.ek_for_cell("Herbivores")
    ek_carnivores = basic_jungle.ek_for_cell("Carnivores")
    assert ek_herbivores == 1
    assert ek_carnivores == 0.18


# natural death


def test_natural_death_in_all_cells(low_fitness_animals):
    """Test that animals with death probability: omega(1 - fitness) = 1 dies"""
    low_fitness_animals.natural_death_all_animals_in_cell()
    assert len(low_fitness_animals.herbivore_list) == 0
    assert len(low_fitness_animals.carnivore_list) == 0


# set parameters


def test_set_parameters_in_a_cell():
    """Testing the method "set parameters" for a jungle and savanna cell"""
    with pytest.raises(ValueError):
        topo.Jungle.set_parameters({"fmax": 100})
    with pytest.raises(ValueError):
        topo.Jungle.set_parameters({"f_max": -100})
    with pytest.raises(ValueError):
        topo.Savanna.set_parameters({"fmax": 100})
    with pytest.raises(ValueError):
        topo.Savanna.set_parameters({"f_max": -100})
    topo.Jungle.set_parameters({"f_max": 800})
    topo.Savanna.set_parameters({"f_max": 300})
    assert topo.Jungle.parameters["f_max"] == 800
    assert topo.Savanna.parameters["f_max"] == 300


# feeding in cell


def test_remove_carnivore():
    jungle_cell = topo.Jungle()
    test_carnivore = animals.Carnivores()
    jungle_cell.add_animal(test_carnivore)
    assert test_carnivore in animals.Animals.instances
    assert test_carnivore in jungle_cell.carnivore_list
    jungle_cell.remove_animal(test_carnivore)
    assert test_carnivore in animals.Animals.instances
    assert test_carnivore not in jungle_cell.carnivore_list
    animals.Animals.instances.remove(test_carnivore)
    assert test_carnivore not in animals.Animals.instances


def test_remove_herbivore():
    savanna_cell = topo.Savanna()
    test_herbivore = animals.Herbivores()
    savanna_cell.add_animal(test_herbivore)
    assert test_herbivore in savanna_cell.herbivore_list
    assert test_herbivore in animals.Animals.instances
    savanna_cell.remove_animal(test_herbivore)
    assert test_herbivore not in savanna_cell.herbivore_list
    assert test_herbivore in animals.Animals.instances
    animals.Animals.instances.remove(test_herbivore)
    assert test_herbivore not in animals.Animals.instances


def test_feeding_herbivores_in_a_cell():
    """ Tests the method "test_feeding_herbivores_in_a_cell" where the
    least fittest animal shall in not be able to eat, due to overgrazing,
    and therefore keep the same weight after the graze commando"""
    jungle_cell = topo.Jungle()
    animals.Herbivores.parameters["sigma_birth"] = 1.5
    [jungle_cell.add_animal(animals.Herbivores()) for _ in range(81)]
    herbivore_fitness_sort = sorted(jungle_cell.herbivore_list,
                                    key=lambda herbi: herbi.fitness)
    assert herbivore_fitness_sort[0].fitness < \
        herbivore_fitness_sort[30].fitness
    least_fittest_herb = herbivore_fitness_sort[0]
    second_least_fittest_herb = herbivore_fitness_sort[1]
    least_fittest_weight = least_fittest_herb.weight
    second_least_fittest_weight = second_least_fittest_herb.weight
    jungle_cell.feed_herbivores_in_cell()
    assert least_fittest_weight == least_fittest_herb.weight
    assert second_least_fittest_weight != second_least_fittest_herb.weight
    # Test that the available fodder now are = 0, and that the increase_fodder
    # works, so the food level again = f_max
    assert jungle_cell.fodder == 0
    jungle_cell.increase_fodder()
    assert jungle_cell.fodder == 800


def test_increase_fodder_savanna_fodder_is_max():
    """Test that the 'increase_fodder' method works at a savanna cell"""
    cell = topo.Savanna()
    cell.increase_fodder()
    assert cell.fodder == 300


def test_feeding_carnivores_in_a_cell():
    """Tests if the most fit herbivore kills the least fit herbivore etc"""
    animals.Carnivores.set_parameters({"DeltaPhiMax": 0.1})
    jungle_cell = topo.Jungle()
    [jungle_cell.add_animal(animals.Herbivores()) for _ in range(10)]
    [jungle_cell.add_animal(animals.Carnivores(weight=80)) for _ in range(10)]
    assert jungle_cell.biomass_carnivores() == 800
    pre_feeding_herbi_biomass = jungle_cell.biomass_herbivores()
    jungle_cell.feed_carnivores_in_cell()
    assert pre_feeding_herbi_biomass > jungle_cell.biomass_herbivores()
