from biosim.Island import Island
import pytest

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

def test_populate_island(standard_map):
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
    surrounding_ocean_cell.migrate_herbivores()
    assert len(surrounding_ocean_cell.raster_model[(1,18)].herbivore_list) == 2
    assert len(surrounding_ocean_cell.raster_model[(1,19)].herbivore_list) == 0

@pytest.fixture
def surrounding_ocean_cell():
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

def test_surrounded_by_occean(surrounding_ocean_cell):
    surrounding_ocean_cell.migrate_herbivores()
    assert len(surrounding_ocean_cell.raster_model[(1,1)].herbivore_list) == 2

def test_find_neighbouring_cells(surrounding_ocean_cell):
    assert surrounding_ocean_cell.find_neighbouring_cells([1,1]) == [(2,1),(0,1),(1,2),(1,0)]
    assert surrounding_ocean_cell.find_neighbouring_cells([1,1]) != [(0,1),(2,1),(1,2),(1,0)]


@pytest.fixture
def mock_ek_and_neighbouring_cells():
    neighbouring_cells = [(11,10),(9,10),(10,11),(10,9)]
    herbivore_ek = {(11,10): 0}
    return neighbouring_cells, herbivore_ek

def test_what_cell(standard_map, mock_ek_and_neighbouring_cells):
    neighbouring_cells, herbivore_ek = mock_ek_and_neighbouring_cells
    te = standard_map.what_cell_to_migrate_to(neighbouring_cells, herbivore_ek)
    assert te == (11,10)


