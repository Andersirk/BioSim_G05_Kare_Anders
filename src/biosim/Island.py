# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

from src.biosim.cell_topography import Jungle, Ocean, Savanna, Mountain, Desert
from src.biosim.animals import Herbivores, Carnivores, Animals
import numpy as np
import copy
import random


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

    def migrate_all_cells(self):
        carnivore_ek, herbivore_ek = self.generate_ek_for_board()
        for location, cell in self.raster_model.items():
            if cell.is_accessible:
                cell.migrate_all_animals_in_cell(self, location, carnivore_ek, herbivore_ek)
        Animals.reset_migration_attempt()

    def generate_ek_for_board(self):
        carnivore_ek = {}
        herbivore_ek = {}
        for location, cell in self.raster_model.items():
            if cell.is_accessible:
                carnivore_ek[location] = cell.ek_for_cell("Carnivores")
                herbivore_ek[location] = cell.ek_for_cell("Herbivores")
        return carnivore_ek, herbivore_ek

    def feed_all_animals(self):
        for cell in self.raster_model.values():
            if cell.__class__.__name__ == "Jungle" or cell.__class__.__name__ == "Savanna":
                cell.feed_herbivores_in_cell()
        for cell in self.raster_model.values():
            if cell.is_accessible:
                cell.feed_carnivores_in_cell()

    def increase_fodder_all_cells(self):
        for cell in self.raster_model.values():
            if cell.__class__.__name__ == "Jungle" or cell.__class__.__name__ == "Savanna":
                cell.increase_fodder()

    def annual_death_all_cells(self):
        for cell in self.raster_model.values():
            if cell.is_accessible:
                cell.natural_death_all_animals_in_cell()

    def breed_in_all_cells(self):
        for cell in self.raster_model.values():
            if cell.is_accessible:
                cell.breed_all_animals_in_cell()

    def annual_cycle(self):
        self.increase_fodder_all_cells()
        self.feed_all_animals()
        self.breed_in_all_cells()
        self.migrate_all_cells()
        Animals.age_up()
        Animals.annual_metabolism()
        self.annual_death_all_cells()









if __name__ == "__main__":
    random.seed(1)
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
               'age': 0, 'weight': 80},
              {'species': 'Herbivore',
               'age': 0, 'weight': 80.3},
                   {'species': 'Herbivore',
                    'age': 0, 'weight': 80.5},
                   {'species': 'Herbivore',
                    'age': 0, 'weight': 10.5}]}])

    island.populate_island([{'loc': (1, 18), 'pop': [{'species': 'Herbivore', 'age': 0, 'weight': 80} for _ in range(100)]}])

    for x in range(50):
        island.annual_cycle()
        print("year", x)
        print("total ani", len(Animals.instances))
        print(len(island.raster_model[(1,18)].herbivore_list))
        print(island.raster_model[(1,18)].biomass_herbivores())
        print("############")






