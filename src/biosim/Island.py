# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

from biosim.cell_topography import Jungle, Ocean, Savanna, Mountain, Desert
from biosim.animals import Herbivores, Carnivores, Animals
import numpy as np

class Island:
    def __init__(self, island_map):
        self.raster_model = self.create_map(island_map)

    def create_map(self, island_map):
        """ Creates a dictionary where the keys are coordinates and values
        are a class with the relevant topography category.

        :param island_map:
        :return dictinary,
        """
        island_map_no_spaces = island_map.replace(" ", "")
        x, y = 0, -1
        raster_model = {}
        for number, landscape_code in enumerate(island_map_no_spaces):
            y += 1
            if landscape_code == "D":
                raster_model[(x, y)] = Desert()
            elif landscape_code == "J":
                raster_model[(x, y)] = Jungle()
            elif landscape_code == "S":
                raster_model[(x, y)] = Savanna()
            elif landscape_code == "O":
                raster_model[(x, y)] = Ocean()
            elif landscape_code == "M":
                raster_model[(x, y)] = Mountain()
            elif landscape_code == "\n":
                y = -1
                x += 1
            if landscape_code not in ["O", "M", "J", "S", "D", "\n"]:
                raise ValueError("The tiles need to be one of the"
                                 "predetermined tiles: O, M, J, S or D")
        self.check_borders_ocean(raster_model)
        return raster_model

    @staticmethod
    def check_borders_ocean(raster_model):
        max_coordinates = max(raster_model.keys())
        for coordinate, cell_class in raster_model.items():
            if coordinate[0] in [0, max_coordinates[0]]:
                if cell_class.__class__.__name__ != "Ocean":
                    raise ValueError("The border of the map needs to "
                                     "consist solely of ocean tiles")
            elif coordinate[1] in [0, max_coordinates[1]]:
                if cell_class.__class__.__name__ != "Ocean":
                    raise ValueError("The border of the map needs to "
                                     "consist solely of ocean tiles")

    def populate_island(self, population_list):
        for dictionary in population_list:
            if dictionary["loc"] not in self.raster_model.keys():
                raise ValueError("These coordinates do not exist in this map's coordiante system.")
            if self.raster_model[dictionary["loc"]].is_accessible:
                for population in dictionary["pop"]:
                    if population["species"] == "Herbivore":
                        self.raster_model[dictionary["loc"]].add_animal(Herbivores(dictionary["loc"], age=population["age"], weight=population["weight"]))
                    elif population["species"] == "Carnivore":
                        self.raster_model[dictionary["loc"]].add_animal(Carnivores(dictionary["loc"], age=population["age"], weight=population["weight"]))
            else:
                raise ValueError(f"An animal cannot be placed on a {self.raster_model[dictionary['loc']].__class__.__name__} cell")

    def migrate_herbivores(self):
        herbivore_ek = {}
        last_years_raster_model = self.raster_model
        for location, cell in last_years_raster_model.items():
            if cell.is_accessible:
                herbivore_ek[location] = cell.current_fodder() / (
                        (len(cell.herbivore_list) + 1
                         ) * Herbivores.parameters["F"])
        for location, cell in last_years_raster_model.items():
            for animal in cell.herbivore_list:
                neighbouring_cells = self.find_neighbouring_cells(location)
                cell_to_migrate = self.what_cell_to_migrate_to(
                                            neighbouring_cells, herbivore_ek)
                self.raster_model[location].remove_animal(animal)
                self.raster_model[cell_to_migrate].add_animal(animal)



    def what_cell_to_migrate_to(self, neighbouring_cells, herbivore_ek):
        sum_ek_neighbours = 0
        cell_probability = []
        for cell in neighbouring_cells:
            sum_ek_neighbours += herbivore_ek[cell]
        for cell in neighbouring_cells:
            cell_probability.append(herbivore_ek[cell]/sum_ek_neighbours)
        cumumlative_probability = np.cumsum(cell_probability)
        rand_num = np.random.random()
        n = 0
        while rand_num >= cumumlative_probability[n]:
            n += 1
        return neighbouring_cells[n]


    def find_neighbouring_cells(self, coordinates):
        neighbouring_cells = [(coordinates[0]+1, coordinates[1]),
                              (coordinates[0]-1, coordinates[1]),
                              (coordinates[0], coordinates[1]+1),
                              (coordinates[0], coordinates[1]-1)]
        return neighbouring_cells






if __name__ == "__main__":
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
    terk = [{'loc': (1, 12),
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

    island.populate_island(terk)
    print(island.raster_model[(3,4)].animals)
    print(island.raster_model[(3,4)].animals[0].__dict__)
    print(island.raster_model[(3,4)].animals[1].__dict__)
    print(island.raster_model[(3,4)].animals[2].__dict__)
    print(Animals.instances[0].__dict__)



