# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

from src.biosim.cell_topography import Jungle, Ocean, Savanna, Mountain, Desert
from src.biosim.animals import Herbivores, Carnivores, Animals
import numpy as np
import copy


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
                if x != 0 and y != previous_y_max:
                    raise ValueError("The board needs to be uniform.")
                previous_y_max = y
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
                        self.raster_model[dictionary["loc"]].add_animal(Herbivores(age=population["age"], weight=population["weight"]))
                    elif population["species"] == "Carnivore":
                        self.raster_model[dictionary["loc"]].add_animal(Carnivores(age=population["age"], weight=population["weight"]))
            else:
                raise ValueError(f"An animal cannot be placed on a {self.raster_model[dictionary['loc']].__class__.__name__} cell")

    def migrate_all_herbivores(self):
        herbivore_ek = {}
        last_years_raster_model = copy.copy(self.raster_model)
        for location, cell in last_years_raster_model.items():
            if cell.is_accessible:
                herbivore_ek[location] = cell.current_fodder() / (
                        (len(cell.herbivore_list) + 1
                         ) * Herbivores.parameters["F"])
        for location, cell in last_years_raster_model.items():
            if cell.is_accessible:
                cell_list = copy.copy(cell.herbivore_list)
                for animal in cell_list:
                    cell_to_migrate = self.what_cell_to_migrate_to(
                                                location, herbivore_ek)
                    self.raster_model[location].remove_animal(animal)
                    self.raster_model[cell_to_migrate].add_animal(animal)


    def what_cell_to_migrate_to(self, current_cell, ek_dict):
        sum_ek_neighbours = 0
        cell_probability = []
        neighbouring_cells = self.find_neighbouring_cells(current_cell)
        original_neighbouring_cells = copy.deepcopy(neighbouring_cells)
        for cell in original_neighbouring_cells:
            if cell not in ek_dict.keys():
                neighbouring_cells.remove(cell)
        for cell in neighbouring_cells:
            sum_ek_neighbours += ek_dict[cell]
        for cell in neighbouring_cells:
            cell_probability.append(ek_dict[cell]/sum_ek_neighbours)
        cumulative_probability = np.cumsum(cell_probability)
        rand_num = np.random.random()
        if len(neighbouring_cells) == 0:
            return current_cell
        n = 0
        while rand_num >= cumulative_probability[n]:
            n += 1
        return neighbouring_cells[n]

    def migrate_all_carnivores(self):
        carnivore_ek = {}
        last_years_raster_model = copy.copy(self.raster_model)
        for location, cell in last_years_raster_model.items():
            if cell.is_accessible:
                carnivore_ek[location] = cell.weight_of_all_herbivores() / (
                        (len(cell.carnivore_list) + 1
                         ) * Carnivores.parameters["F"])
        for location, cell in last_years_raster_model.items():
            if cell.is_accessible:
                cell_list = copy.copy(cell.carnivore_list)
                for animal in cell_list:
                    cell_to_migrate = self.what_cell_to_migrate_to(
                                                location, carnivore_ek)
                    self.raster_model[location].remove_animal(animal)
                    self.raster_model[cell_to_migrate].add_animal(animal)


    def find_neighbouring_cells(self, coordinates):
        neighbouring_cells = [(coordinates[0]+1, coordinates[1]),
                              (coordinates[0]-1, coordinates[1]),
                              (coordinates[0], coordinates[1]+1),
                              (coordinates[0], coordinates[1]-1)]
        return neighbouring_cells

    def feed_all_animals(self):
        for cell in self.raster_model.items():
            if cell.__class__.__name__ == "Jungle" or cell.__class__.__name__ == "Savanna":
                cell.feeding_herbivores()
        for cell in self.raster_model.items():
            if cell.is_accessible:
                cell.feeding_carnivores()


    def increase_fodder_all_cells(self):
        for cell in self.raster_model.items():
            if cell.__class__.__name__ == "Jungle" or cell.__class__.__name__ == "Savanna":
                cell.increase_fodder()

    def annual_death_all_cells(self):
        for cell in self.raster_model.items():
            if cell.is_accessible:
                cell.natural_death()


    def annual_cycle(self):
        self.increase_fodder_all_cells()
        self.feed_all_animals()
        self.annual_death_all_cells()
        self.migrate_all_herbivores()
        self.migrate_all_carnivores()
        Animals.age_up()
        Animals.annual_weight_decrease()








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
    island.populate_island([{'loc': (1, 18),
           'pop': [{'species': 'Herbivore',
               'age': 10, 'weight': 12.5},
              {'species': 'Herbivore',
               'age': 9, 'weight': 10.3},
                   {'species': 'Herbivore',
                    'age': 10, 'weight': 25.5},
                   {'species': 'Herbivore',
                    'age': 10, 'weight': 20.5}]}])
    for x in island.raster_model[(1,18)].herbivore_list:
        print (x.fitness)

    print("##############")
    list = sorted(island.raster_model[(1,18)].herbivore_list, key=lambda x: x.fitness)

    for x in list:
        print(x.fitness)


