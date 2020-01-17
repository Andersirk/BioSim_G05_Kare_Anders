from biosim.Island import Island
import src.biosim.cell_topography as topo
import src.biosim.animals as ani
import pytest

# Map generation
@pytest.fixture
def standard_map():
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

def test_populate_island_acceptable_cells(standard_map):
    population = [{'loc': (1, 14),
      'pop': [{'species': 'Herbivore',
               'age': 10, 'weight': 12.5},
              {'species': 'Herbivore',
               'age': 9, 'weight': 10.3},
              {'species': 'Carnivore',
               'age': 5, 'weight': 8.1}]},
     {'loc': (4, 4),
      'pop': [{'species': 'Herbivore',
               'age': 10, 'weight': 12.5},
              {'species': 'Carnivore',
               'age': 3, 'weight': 7.3},
              {'species': 'Carnivore',
               'age': 5, 'weight': 8.1}]}]
    standard_map.populate_island(population)
    assert len(standard_map.raster_model[(1,14)].herbivore_list) == 2

def test_populate_island_ocean_cell_raises_valueerror(standard_map):
    with pytest.raises(ValueError):
        population = [{'loc': (1, 3),
          'pop': [{'species': 'Herbivore',
                   'age': 10, 'weight': 12.5},
                  {'species': 'Herbivore',
                   'age': 9, 'weight': 10.3},
                  {'species': 'Carnivore',
                   'age': 5, 'weight': 8.1}]}]
        standard_map.populate_island(population)

def test_populate_island_nonexistant_coordinates(standard_map):
    with pytest.raises(ValueError):
        population = [{'loc': (-1, 3),
          'pop': [{'species': 'Herbivore',
                   'age': 10, 'weight': 12.5},
                  {'species': 'Herbivore',
                   'age': 9, 'weight': 10.3},
                  {'species': 'Carnivore',
                   'age': 5, 'weight': 8.1}]}]
        standard_map.populate_island(population)

def test_populate_island_float_age(standard_map):
    with pytest.raises(ValueError):
        population = [{'loc': (4, 7),
          'pop': [{'species': 'Herbivore',
                   'age': 10.5, 'weight': 12.5},
                  {'species': 'Carnivore',
                   'age': 5, 'weight': 8.1}]}]
        standard_map.populate_island(population)

def test_populate_island_negative_age(standard_map):
    with pytest.raises(ValueError):
        population = [{'loc': (4, 7),
          'pop': [{'species': 'Herbivore',
                   'age': 10, 'weight': 12.5},
                  {'species': 'Carnivore',
                   'age': -1, 'weight': 8.1}]}]
        standard_map.populate_island(population)

def test_populate_island_negative_weight(standard_map):
    with pytest.raises(ValueError):
        population = [{'loc': (4, 7),
          'pop': [{'species': 'Herbivore',
                   'age': 10, 'weight': 12.5},
                  {'species': 'Carnivore',
                   'age': 1, 'weight': -10.2}]}]
        standard_map.populate_island(population)

def test_populate_island_0_weight(standard_map):
    with pytest.raises(ValueError):
        population = [{'loc': (4, 7),
          'pop': [{'species': 'Herbivore',
                   'age': 10, 'weight': 12.5},
                  {'species': 'Carnivore',
                   'age': 1, 'weight': 0}]}]
        standard_map.populate_island(population)

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
def surrounding_ocean_cell_small():
    geogr = """\
                OOOOO
                OJMDO
                OMMMO
                OMDMO
                OOOOO"""
    island = Island(geogr)
    island.populate_island([{'loc': (1, 1), 'pop': [{'species': 'Herbivore', 'age': 0, 'weight': 10} for _ in range(10)]}])
    island.populate_island([{'loc': (1, 3), 'pop': [{'species': 'Herbivore', 'age': 0, 'weight': 10} for _ in range(10)]}])
    island.populate_island([{'loc': (3, 2), 'pop': [{'species': 'Carnivore', 'age': 0, 'weight': 80} for _ in range(100)]}])
    island.populate_island([{'loc': (3, 2), 'pop': [{'species': 'Herbivore', 'age': 100, 'weight': 1}]}])
    return island


def test_migration_cant_happen(surrounding_ocean_cell_small):
    """The test shows that the animals dont migrate when their cell is
    surrounded by non-accessible cells"""
    surrounding_ocean_cell_small.migrate_all_cells()
    assert len(surrounding_ocean_cell_small.raster_model[(1, 1)].herbivore_list) == 10
    assert len(surrounding_ocean_cell_small.raster_model[(1, 3)].herbivore_list) == 10

# feeding and fodder

def test_feed_all_animals(surrounding_ocean_cell_small):
    """Test if the herbivores and the carnivores eat."""
    biomass_before_feeding_1_1 = topo.Topography.biomass_herbivores(surrounding_ocean_cell_small.raster_model[(1, 1)])
    biomass_before_feeding_1_3 = topo.Topography.biomass_herbivores(surrounding_ocean_cell_small.raster_model[(1, 3)])
    surrounding_ocean_cell_small.feed_all_animals()
    biomass_after_feeding_1_1 = topo.Topography.biomass_herbivores(surrounding_ocean_cell_small.raster_model[(1, 1)])
    biomass_after_feeding_1_3 = topo.Topography.biomass_herbivores(surrounding_ocean_cell_small.raster_model[(1, 3)])
    assert biomass_before_feeding_1_1 != biomass_after_feeding_1_1
    assert biomass_before_feeding_1_3 == biomass_after_feeding_1_3
    assert len(surrounding_ocean_cell_small.raster_model[(3, 2)].herbivore_list) == 0

def test_increase_fodder_random_jungle_cells(standard_map):
    standard_map.raster_model[(4, 7)].fodder = 0
    standard_map.raster_model[(11, 8)].fodder = 45
    standard_map.increase_fodder_all_cells()
    assert standard_map.raster_model[(4, 7)].fodder == topo.Jungle.parameters["f_max"]
    assert standard_map.raster_model[(11, 8)].fodder == topo.Jungle.parameters["f_max"]

# annual death

def test_annual_death_0_fitness_random_cells(standard_map):
    standard_map.raster_model[(3, 4)].add_animal(ani.Herbivores(age=100, weight=0))
    standard_map.raster_model[(11, 8)].add_animal(ani.Carnivores(age=100, weight=0))
    standard_map.annual_death_all_cells()
    assert standard_map.raster_model[(3, 4)].herbivore_list == []
    assert standard_map.raster_model[(11, 8)].carnivore_list == []

def test_breed_all_cells_certain_prob_random_cell(standard_map):
    for _ in range(100):
        standard_map.raster_model[(3, 4)].add_animal(ani.Herbivores(age=0, weight=100))
        standard_map.raster_model[(11, 8)].add_animal(ani.Carnivores(age=0, weight=100))
    standard_map.breed_in_all_cells()
    assert len(standard_map.raster_model[(3, 4)].herbivore_list) == 200
    assert len(standard_map.raster_model[(11, 8)].carnivore_list) == 200






