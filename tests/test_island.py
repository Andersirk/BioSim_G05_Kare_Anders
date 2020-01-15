from biosim.Island import Island
import src.biosim.cell_topography as topo
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

def test_empty_island():
    """Empty island can be created"""
    Island(island_map="OO\nOO")


def test_minimal_island():
    """Island of single jungle cell"""
    Island(island_map="OOO\nOJO\nOOO")


def test_all_types():
    """All types of landscape can be created"""
    Island(island_map="OOOO\nOJSO\nOMDO\nOOOO")


@pytest.mark.parametrize("bad_boundary", ["J", "S", "M", "D"])
def test_invalid_boundary(bad_boundary):
    """Non-ocean boundary must raise error"""
    with pytest.raises(ValueError):
        Island(island_map="{}OO\nOJO\nOOO".format(bad_boundary))


def test_invalid_landscape():
    """Invalid landscape type must raise error"""
    with pytest.raises(ValueError):
        Island(island_map="OOO\nORO\nOOO")


def test_inconsistent_length():
    """Inconsistent line length must raise error"""
    with pytest.raises(ValueError):
        Island(island_map="OOO\nOJJO\nOOO")


def test_inconsistent_height():
    """Inconsistent line length must raise error"""
    with pytest.raises(ValueError):
        Island(island_map="OOO\nOJO\nOOO\nOO")


#Migration

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
    island = Island(geogr)
    occupants = [{'loc': (1, 19),
           'pop': [{'species': 'Herbivore',
               'age': 10, 'weight': 12.5},
              {'species': 'Herbivore',
               'age': 9, 'weight': 10.3}]}]
    island.populate_island(occupants)
    return island

def test_one_option_migration(surrounding_ocean_cell):
    surrounding_ocean_cell.migrate_all_cells()
    assert len(surrounding_ocean_cell.raster_model[(1, 18)].herbivore_list) == 2
    assert len(surrounding_ocean_cell.raster_model[(1, 19)].herbivore_list) == 0

@pytest.fixture
def surrounding_ocean_cell_small():
    geogr = """\
                OOO
                OSO
                OOO"""
    island = Island(geogr)
    occupants = [{'loc': (1, 1),
           'pop': [{'species': 'Herbivore',
               'age': 10, 'weight': 12.5},
              {'species': 'Herbivore',
               'age': 9, 'weight': 10.3}]}]
    island.populate_island(occupants)
    return island

def test_surrounded_by_occean(surrounding_ocean_cell_small):
    surrounding_ocean_cell_small.migrate_all_cells()
    assert len(surrounding_ocean_cell_small.raster_model[(1,1)].herbivore_list) == 2


