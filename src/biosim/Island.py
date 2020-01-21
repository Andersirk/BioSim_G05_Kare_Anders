# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

from biosim.cell_topography import Jungle, Ocean, Savanna, Mountain, Desert
from biosim.animals import Herbivores, Carnivores, Animals
import pandas as pd
import numpy as np


class Island:
    """This is the overall class for the global events on Rossumøya"""
    def __init__(self, island_map):
        self.raster_model = self.create_map(island_map)
        self.current_year = 0

    def create_map(self, island_map):
        """
        Creates a dictionary where the keys are coordinates and values
        are a class with the relevant topography category.
        :param island_map: multistring
        :return dictionary
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
        """
        Checks if the characters in the outer limits of the multistring, that
        forms the map, consist only of 'O' (Ocean)
        :param raster_model: multistring
        :return: None
        """
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
        """
        Populates an specific accessible cell on the island with instances
        of an animal-class.
        :param population_list: list of dictionary [{cell-coordinates,
        instance}]
        :return: None
        """
        for dictionary in population_list:
            self._check_new_population_age_and_weight(dictionary)
            if dictionary["loc"] not in self.raster_model.keys():
                raise ValueError("These coordinates do not exist in this map's"
                                 " coordinate system.")
            if self.raster_model[dictionary["loc"]].is_accessible:
                for population in dictionary["pop"]:
                    if population["species"] == "Herbivore":
                        self.raster_model[dictionary["loc"]].add_animal(
                            Herbivores(age=population["age"],
                                       weight=population["weight"]))
                    elif population["species"] == "Carnivore":
                        self.raster_model[dictionary["loc"]].add_animal(
                            Carnivores(age=population["age"],
                                       weight=population["weight"]))
            else:
                raise ValueError(f"An animal cannot be placed on a {self.raster_model[dictionary['loc']].__class__.__name__} cell")

    def _check_new_population_age_and_weight(self, new_population_dict):
        """
        Controls that the variables in the the new population are allowed.
        :param new_population_dict: [{cell-coordinates,
        instance}]
        :return: None
        """
        for animal in new_population_dict["pop"]:
            if type(animal["age"]) != int or animal["age"] < 0:
                raise ValueError("The animals age must be a non-negative integer")
            if animal["weight"] is not None:
                if animal["weight"] <= 0:
                    raise ValueError("The animal must have a positive weight")

    def _migrate_all_cells(self):
        """
        Makes all instances in all cell on the island try to migrate.
        :return: None
        """
        carnivore_ek, herbivore_ek = self._generate_ek_for_board()
        for location, cell in self.raster_model.items():
            if cell.is_accessible:
                cell.migrate_all_animals_in_cell(self, location, carnivore_ek, herbivore_ek)
        Animals.reset_migration_attempt()

    def _generate_ek_for_board(self):
        """
        Generates carnivore and herbivore ek for all accessible cells on the
        island
        :return: carnivore_ek and herbivore_ek as floats
        """
        carnivore_ek = {}
        herbivore_ek = {}
        for location, cell in self.raster_model.items():
            if cell.is_accessible:
                carnivore_ek[location] = cell.ek_for_cell("Carnivores")
                herbivore_ek[location] = cell.ek_for_cell("Herbivores")
        return carnivore_ek, herbivore_ek

    def _feed_all_animals(self):
        """
        Makes all animals in all accessible cells try to eat
        :return: None
        """
        for cell in self.raster_model.values():
            if cell.__class__.__name__ == "Jungle" or cell.__class__.__name__ == "Savanna":
                cell.feed_herbivores_in_cell()
        for cell in self.raster_model.values():
            if cell.is_accessible:
                cell.feed_carnivores_in_cell()

    def _increase_fodder_all_cells(self):
        """
        Increase fodder in all primary producing cells
        :return: None
        """
        for cell in self.raster_model.values():
            if cell.__class__.__name__ == "Jungle" or cell.__class__.__name__ == "Savanna":
                cell.increase_fodder()

    def _annual_death_all_cells(self):
        """
        Runs the annual_death method for all animals in all accessible cells
        :return: None
        """
        for cell in self.raster_model.values():
            if cell.is_accessible:
                cell.natural_death_all_animals_in_cell()

    def _breed_in_all_cells(self):
        """
        Runs the breeding method for all animals in all accessible cells
        :return: None
        """
        for cell in self.raster_model.values():
            if cell.is_accessible:
                cell.breed_all_animals_in_cell()

    def annual_cycle(self):
        """
        Runs all the components of the annual cycle in the correct order
        :return: None
        """
        self._increase_fodder_all_cells()
        self._feed_all_animals()
        self._breed_in_all_cells()
        self._migrate_all_cells()
        Animals.age_up()
        Animals.annual_metabolism()
        self._annual_death_all_cells()

    def per_cell_count_pandas_dataframe(self):
        """
        Counts the number of herbivores and carnivores in every cell
        :return: dataframe
        """
        pdlist = []
        for coordinate, cell in self.raster_model.items():
            if cell.is_accessible:
                herb_amount = len(cell.herbivore_list)
                carn_amount = len(cell.carnivore_list)
            else:
                herb_amount = 0
                carn_amount = 0
            pdlist.append([coordinate[0], coordinate[1], herb_amount, carn_amount])
        dataframe = pd.DataFrame(pdlist,columns=['Row','Col', 'Herbivore', 'Carnivore'])
        return dataframe

    def arrays_for_heatmap(self):
        """
        Counts the number of herbivores and carnivores in every cell
        :return: numpy arrays
        """
        maxcord = max(self.raster_model.keys())
        herb_array = np.zeros(maxcord)
        carn_array = np.zeros(maxcord)
        for (row, col), instance in self.raster_model.items():
            if instance.is_accessible:
                herb_array[row][col] = len(instance.herbivore_list)
                carn_array[row][col] = len(instance.carnivore_list)
        return herb_array, carn_array

    def total_number_per_species(self):
        """
        Counts the total number of individuals of a species on the island
        :return: dict {species: individuals}
        """
        total_herb = 0
        total_carn = 0
        for cell in self.raster_model.values():
            if cell.is_accessible:
                total_carn += len(cell.carnivore_list)
                total_herb += len(cell.herbivore_list)
        return {'Herbivore': total_herb, 'Carnivore': total_carn}

    def herbivore_biomass_age_groups(self):
        """
        Makes lists of herbivores individuals and the total biomass within the
        age groups 0-1, 2-5, 5-10, 10-15 and 15 +.
        :return: lists
        """
        herbivore_age_numbers = [0, 0, 0, 0, 0]
        herbivore_biomass = [0, 0, 0, 0, 0]
        for cell in self.raster_model.values():
            if cell.is_accessible:
                for herbivore in cell.herbivore_list:
                    if herbivore.age <= 1:
                        herbivore_age_numbers[0] += 1
                        herbivore_biomass[0] += herbivore.weight
                    elif 1 < herbivore.age < 5:
                        herbivore_age_numbers[1] += 1
                        herbivore_biomass[1] += herbivore.weight
                    elif 5 <= herbivore.age < 10:
                        herbivore_age_numbers[2] += 1
                        herbivore_biomass[2] += herbivore.weight
                    elif 10 <= herbivore.age < 15:
                        herbivore_age_numbers[3] += 1
                        herbivore_biomass[3] += herbivore.weight
                    elif herbivore.age >= 15:
                        herbivore_age_numbers[4] += 1
                        herbivore_biomass[4] += herbivore.weight
        return herbivore_age_numbers, herbivore_biomass

    def carnivore_biomass_age_groups(self):
        """
        Makes lists of carnivores individuals and the total biomass within the
        age groups 0-1, 2-5, 5-10, 10-15 and 15 +.
        :return: lists
        """
        carnivore_age_numbers = [0, 0, 0, 0, 0]
        carnivore_biomass = [0, 0, 0, 0, 0]
        for cell in self.raster_model.values():
            if cell.is_accessible:
                for carnivore in cell.carnivore_list:
                    if carnivore.age <= 1:
                        carnivore_age_numbers[0] -= 1
                        carnivore_biomass[0] += carnivore.weight
                    elif 1 < carnivore.age < 5:
                        carnivore_age_numbers[1] -= 1
                        carnivore_biomass[1] += carnivore.weight
                    elif 5 <= carnivore.age < 10:
                        carnivore_age_numbers[2] -= 1
                        carnivore_biomass[2] += carnivore.weight
                    elif 10 <= carnivore.age < 15:
                        carnivore_age_numbers[3] -= 1
                        carnivore_biomass[3] += carnivore.weight
                    elif carnivore.age >= 15:
                        carnivore_age_numbers[4] -= 1
                        carnivore_biomass[4] += carnivore.weight
        return carnivore_age_numbers, carnivore_biomass

    def population_biomass_age_groups(self):
        """
        Uses this information to calculate the average weight within a age group.
        :return: lists where the first index are the age group 0-1 etc.
        """
        herbivore_age_numbers, herbivore_biomass =\
            self.herbivore_biomass_age_groups()
        carnivore_age_numbers, carnivore_biomass = \
            self.carnivore_biomass_age_groups()
        herb_mean_w_list = []
        carn_mean_w_list = []
        for biomass, age in zip(herbivore_biomass, herbivore_age_numbers):
            if age > 0:
                herb_mean_w_list.append(biomass/age)
            else:
                herb_mean_w_list.append(0)
        for biomass, age in zip(carnivore_biomass, carnivore_age_numbers):
            if age < 0:
                carn_mean_w_list.append(biomass/age)
            else:
                carn_mean_w_list.append(0)
        return herbivore_age_numbers, carnivore_age_numbers, herb_mean_w_list, carn_mean_w_list

    def biomass_food_chain(self):
        """
        Calculates the total amount of fodder and the total biomass for the
        herbivores and carnivores.
        :return: dictionary
        """
        biomass_fodder = 0
        biomass_herbs = 0
        biomass_carnivores = 0
        for cell in self.raster_model.values():
            if cell.is_accessible:
                biomass_fodder += cell.fodder
                biomass_herbs += cell.biomass_herbivores()
                biomass_carnivores += cell.biomass_carnivores()
        biomass_dict = {"biomass_fodder":biomass_fodder,
                        "biomass_herbs":biomass_herbs,
                        "biomass_carnivores": biomass_carnivores}
        return biomass_dict

if __name__ == "__main__":
    # random.seed(1)
    # geogr = """\
    #             OOOOOOOOOOOOOOOOOOOOO
    #             OOOOOOOOSMMMMJJJJJJJO
    #             OSSSSSJJJJMMJJJJJJJOO
    #             OSSSSSSSSSMMJJJJJJOOO
    #             OSSSSSJJJJJJJJJJJJOOO
    #             OSSSSSJJJDDJJJSJJJOOO
    #             OSSJJJJJDDDJJJSSSSOOO
    #             OOSSSSJJJDDJJJSOOOOOO
    #             OSSSJJJJJDDJJJJJJJOOO
    #             OSSSSJJJJDDJJJJOOOOOO
    #             OOSSSSJJJJJJJJOOOOOOO
    #             OOOSSSSJJJJJJJOOOOOOO
    #             OOOOOOOOOOOOOOOOOOOOO"""
    # island = Island(geogr)
    # island.populate_island([{'loc': (1, 18),
    #        'pop': [{'species': 'Herbivore',
    #            'age': 0, 'weight': 80},
    #           {'species': 'Herbivore',
    #            'age': 0, 'weight': 80.3},
    #                {'species': 'Herbivore',
    #                 'age': 0, 'weight': 80.5},
    #                {'species': 'Herbivore',
    #                 'age': 0, 'weight': 10.5}]}])
    #
    # island.populate_island([{'loc': (1, 18), 'pop': [{'species': 'Herbivore', 'age': 0, 'weight': None} for _ in range(100)]}])
    #
    # for x in range(30):
    #     island.annual_cycle()
    #     print("year", x)
    #     print("total ani", len(Animals.instances))
    #     print(len(island.raster_model[(1,18)].herbivore_list))
    #     print(island.raster_model[(1,18)].biomass_herbivores())
    #     print("############")
    #
    # island.populate_island([{'loc': (1, 17), 'pop': [{'species': 'Carnivore', 'age': 0, 'weight': 80} for _ in range(300)]}])
    #
    #
    # for x in range(10):
    #     island.annual_cycle()
    #     print("year", x)
    #     print("total ani", len(Animals.instances))
    #     total_herb = 0
    #     total_carn = 0
    #     for cell in island.raster_model.values():
    #         if cell.is_accessible:
    #             total_carn += len(cell.carnivore_list)
    #             total_herb += len(cell.herbivore_list)
    #     print("total herbs:", total_herb)
    #     print("total carns:", total_carn)
    #     print(len(island.raster_model[(1, 18)].herbivore_list))
    #     print(island.raster_model[(1, 18)].biomass_herbivores())
    #     print("############")
    #
    #
    # print(island.array_for_heatmap())
    # # island.pandas_dataframe()
    # print(island.population_age_grups())
    # # island.population_pyramid()
    # print(island.biomass_food_chain())
    island_map = """\
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

    ini_pop = [{'loc': (1, 18), 'pop': [
        {'species': 'Herbivore', 'age': 0, 'weight': 80} for _ in
        range(100)]},
               {'loc': (11, 8), 'pop': [
                   {'species': 'Carnivore', 'age': 0, 'weight': 80} for _ in
                   range(100)]}
               ]
    island = Island(island_map)
    island.populate_island(ini_pop)
    for _ in range (20):
        island.annual_cycle()
        print(island.population_age_grups())
        print(island.total_number_per_species().values())
        print("#############")
    ini_pop2 = [{'loc': (1, 17), 'pop': [
        {'species': 'Carnivore', 'age': 0, 'weight': 80} for _ in
        range(100)]},
               {'loc': (1, 18), 'pop': [
                   {'species': 'Carnivore', 'age': 0, 'weight': 80} for _ in
                   range(100)]}
               ]
    island.populate_island(ini_pop2)
    for _ in range (50):
        island.annual_cycle()
        print(island.population_age_grups())
        print(island.total_number_per_species().values())
        print("#############")
