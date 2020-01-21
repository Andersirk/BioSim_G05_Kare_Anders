from biosim.Island import Island
import biosim.cell_topography as topo
import biosim.animals as ani
import pytest
import numpy as np

# Map generation
@pytest.fixture
def test_map():
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
    island = Island(geogr)
    return island


def test_populate_island_acceptable_cells(test_map):
    """Test that animals can be placed on every accessible cell"""
    population = [{'loc': (1, 14),
                   'pop': [{'species': 'Herbivore', 'age': 9, 'weight': 13}]},
                  {'loc': (1, 8),
                   'pop': [{'species': 'Herbivore', 'age': 10, 'weight': 13}]},
                  {'loc': (5, 10), 'pop': [{'species': 'Carnivore', 'age': 10,
                                            'weight': 12.5}]}]
    test_map.populate_island(population)
    assert len(test_map.raster_model[(1, 14)].herbivore_list) == 1
    assert len(test_map.raster_model[(1, 8)].herbivore_list) == 1
    assert len(test_map.raster_model[(5, 10)].carnivore_list) == 1


def test_populate_island_ocean_cell_raises_value_error(test_map):
    """Test that a value error raises if an animal are placed on a non-
    accessible cell"""
    with pytest.raises(ValueError):
        population = [{'loc': (1, 3),
                       'pop': [{'species': 'Herbivore', 'age': 9, 'weight': 9},
                               {'species': 'Herbivore', 'age': 9, 'weight': 9},
                               {'species': 'Carnivore', 'age': 5,
                                'weight': 8}]}]
        test_map.populate_island(population)


def test_populate_island_non_existent_coordinates(test_map):
    """Test that a value error raises if an animal are placed on a non-
    existing coordinate"""
    with pytest.raises(ValueError):
        population = [{'loc': (-1, 3),
                       'pop': [{'species': 'Herbivore', 'age': 9, 'weight': 9},
                               {'species': 'Herbivore', 'age': 9, 'weight': 9},
                               {'species': 'Carnivore', 'age': 5,
                                'weight': 8}]}]
        test_map.populate_island(population)


def test_populate_island_float_age(test_map):
    """Test that a value error raises if an animal are created with a float
    number as age"""
    with pytest.raises(ValueError):
        population = [{'loc': (4, 7),
                       'pop': [{'species': 'Herbivore', 'age': 10.5,
                                'weight': 12.5}, {'species': 'Carnivore',
                                                  'age': 5, 'weight': 8.1}]}]
        test_map.populate_island(population)


def test_populate_island_negative_age(test_map):
    """Test if a value error raises if an animal are created with a
    negative age"""
    with pytest.raises(ValueError):
        population = [{'loc': (4, 7),
                       'pop': [{'species': 'Herbivore', 'age': 9, 'weight': 9},
                               {'species': 'Carnivore', 'age': -1,
                                'weight': 8}]}]
        test_map.populate_island(population)


def test_populate_island_0_weight(test_map):
    """Test if a value error raises if an animal are created with weight = 0"""
    with pytest.raises(ValueError):
        population = [{'loc': (4, 7),
                       'pop': [{'species': 'Herbivore', 'age': 9, 'weight': 9},
                               {'species': 'Carnivore', 'age': 1,
                                'weight': 0}]}]
        test_map.populate_island(population)


def test_empty_island():
    """Empty island can be created"""
    Island("OO\nOO")


def test_minimal_island():
    """Island of single jungle cell"""
    Island("OOO\nOJO\nOOO")


def test_all_types():
    """All types of landscape can be created"""
    Island("OOOO\nOJSO\nOMDO\nOOOO")


@pytest.mark.parametrize("bad_boundary", ["J", "S", "M", "D"])
def test_invalid_boundary(bad_boundary):
    """Non-ocean boundary must raise error"""
    with pytest.raises(ValueError):
        Island("{}OO\nOJO\nOOO".format(bad_boundary))


def test_invalid_landscape():
    """Invalid landscape type must raise error"""
    with pytest.raises(ValueError):
        Island("OOO\nORO\nOOO")


def test_inconsistent_length():
    """Inconsistent line length must raise error"""
    with pytest.raises(ValueError):
        Island("OOO\nOJJO\nOOO")


def test_inconsistent_height():
    """Inconsistent line length must raise error"""
    with pytest.raises(ValueError):
        Island("OOO\nOJO\nOOO\nOO")


# Migration


@pytest.fixture
def small_island_map():
    geogr = """\
                OOOOO
                OJMDO
                OMMMO
                OMDMO
                OOOOO"""
    island = Island(geogr)
    island.populate_island(
        [{'loc': (1, 1),
          'pop': [{'species': 'Herbivore',
                   'age': 0, 'weight': 10} for _ in range(10)]}])
    island.populate_island(
        [{'loc': (1, 3),
          'pop': [{'species': 'Herbivore', 'age': 0, 'weight': 10}
                  for _ in range(10)]}])
    island.populate_island(
        [{'loc': (3, 2),
          'pop': [{'species': 'Carnivore', 'age': 0, 'weight': 80}
                  for _ in range(100)]}])
    island.populate_island(
        [{'loc': (3, 2),
          'pop': [{'species': 'Herbivore', 'age': 100, 'weight': 1}]}])
    return island


def test_migration_cant_happen(small_island_map):
    """The test shows that the animals dont migrate when their cell is
    surrounded by non-accessible cells"""
    small_island_map._migrate_all_cells()
    assert len(small_island_map.raster_model[(1, 1)].herbivore_list) == 10
    assert len(small_island_map.raster_model[(1, 3)].herbivore_list) == 10


# feeding and fodder


def test_feed_all_animals(small_island_map):
    """Tests if the herbivores and the carnivores eat."""
    biomass_before_feeding_1_1 = topo.Topography.biomass_herbivores(
        small_island_map.raster_model[(1, 1)])
    biomass_before_feeding_1_3 = topo.Topography.biomass_herbivores(
        small_island_map.raster_model[(1, 3)])
    small_island_map._feed_all_animals()
    biomass_after_feeding_1_1 = topo.Topography.biomass_herbivores(
        small_island_map.raster_model[(1, 1)])
    biomass_after_feeding_1_3 = topo.Topography.biomass_herbivores(
        small_island_map.raster_model[(1, 3)])
    assert biomass_before_feeding_1_1 != biomass_after_feeding_1_1
    assert biomass_before_feeding_1_3 == biomass_after_feeding_1_3
    assert len(small_island_map.raster_model[(
        3, 2)].herbivore_list) == 0


def test_increase_fodder_random_jungle_cells(test_map):
    """Tests that the method 'increase_fodder' works in a jungle cell"""
    test_map.raster_model[(4, 7)].fodder = 0
    test_map.raster_model[(11, 8)].fodder = 45
    test_map._increase_fodder_all_cells()
    assert test_map.raster_model[(4, 7)].fodder == topo.Jungle.parameters[
        "f_max"]
    assert test_map.raster_model[(11, 8)].fodder == topo.Jungle.parameters[
        "f_max"]


# annual death


def test_annual_death_0_fitness_random_cells(test_map):
    """Tests that the method annual_death works in a random accessible cell"""
    test_map.raster_model[(3, 4)].add_animal(ani.Herbivores(age=99, weight=0))
    test_map.raster_model[(11, 8)].add_animal(ani.Carnivores(age=99, weight=0))
    test_map._annual_death_all_cells()
    assert test_map.raster_model[(3, 4)].herbivore_list == []
    assert test_map.raster_model[(11, 8)].carnivore_list == []


def test_breed_all_cells_certain_prob_random_cell(test_map):
    """Test that the method 'breed_all_cell' works in a random accessible
     cell"""
    for _ in range(100):
        test_map.raster_model[(3, 4)].add_animal(ani.Herbivores(
            age=0, weight=100))
        test_map.raster_model[(11, 8)].add_animal(ani.Carnivores(
            age=0, weight=100))
    test_map._breed_in_all_cells()
    assert len(test_map.raster_model[(3, 4)].herbivore_list) == 200
    assert len(test_map.raster_model[(11, 8)].carnivore_list) == 200


def test_population_age_groups(test_map):
    """Tests that the method population_age_groups returns two arrays and two
    lists"""
    test_map.raster_model[(3, 4)].add_animal(ani.Herbivores(age=1, weight=10))
    test_map.raster_model[(3, 4)].add_animal(ani.Herbivores(age=4, weight=10))
    test_map.raster_model[(3, 4)].add_animal(ani.Herbivores(age=9, weight=10))
    test_map.raster_model[(3, 4)].add_animal(ani.Herbivores(age=14, weight=10))
    test_map.raster_model[(3, 4)].add_animal(ani.Herbivores(age=50, weight=10))
    test_map.raster_model[(3, 4)].add_animal(ani.Carnivores(age=1, weight=10))
    test_map.raster_model[(3, 4)].add_animal(ani.Carnivores(age=4, weight=10))
    test_map.raster_model[(3, 4)].add_animal(ani.Carnivores(age=9, weight=10))
    test_map.raster_model[(3, 4)].add_animal(ani.Carnivores(age=14, weight=10))
    test_map.raster_model[(3, 4)].add_animal(ani.Carnivores(age=50, weight=10))
    herb_list, carn_list, herb_mean_w_list, carn_mean_w_list = \
        test_map.population_biomass_age_groups()
    assert herb_list == [1, 1, 1, 1, 1]
    assert carn_list == [-1, -1, -1, -1, -1]
    assert herb_mean_w_list == [10, 10, 10, 10, 10]
    assert carn_mean_w_list == [-10, -10, -10, -10, -10]


def test_biomass_food_chain(test_map):
    """Tests that the method biomass_food_chain returns a dictionary with the
    correct islands total biomass of fodder, herbivores and carnivores"""
    test_map.raster_model[(3, 4)].add_animal(ani.Herbivores(age=99, weight=10))
    test_map.raster_model[(3, 4)].add_animal(ani.Carnivores(age=1, weight=100))
    for cell in test_map.raster_model.values():
        if cell.is_accessible:
            cell.fodder = 0
    biomass_dict = test_map.biomass_food_chain()
    assert biomass_dict.get('biomass_fodder') == 0
    assert biomass_dict.get('biomass_herbs') == 10
    assert biomass_dict.get('biomass_carnivores') == 100
