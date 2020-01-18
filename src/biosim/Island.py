# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

from biosim.cell_topography import Jungle, Ocean, Savanna, Mountain, Desert
from biosim.animals import Herbivores, Carnivores, Animals
import copy
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class Island:
    def __init__(self, island_map):
        self.raster_model = self.create_map(island_map)
        self.current_year = 0

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
            self.check_new_population_age_and_weight(dictionary)
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

    def check_new_population_age_and_weight(self, new_population_dict):
        for animal in new_population_dict["pop"]:
            if type(animal["age"]) != int or animal["age"] < 0:
                raise ValueError("The animals age must be a non-negative integer")
            if animal["weight"] is not None:
                if animal["weight"] <= 0:
                    raise ValueError("The animal must have a positive weight")

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
        self.current_year += 1

    def per_cell_count_pandas_dataframe(self):
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

    def total_number_per_species(self):
        total_herb = 0
        total_carn = 0
        for cell in self.raster_model.values():
            if cell.is_accessible:
                total_carn += len(cell.carnivore_list)
                total_herb += len(cell.herbivore_list)
        return {'Herbivore': total_herb, 'Carnivore': total_carn}


    def population_age_grups(self):
        herbivore_0_5, carnivore_0_5 = 0, 0
        herbivore_5_10, carnivore_5_10 = 0, 0
        herbivore_10_15, carnivore_10_15 = 0, 0
        herbivore_15plus, carnivore_15plus = 0, 0
        for cell in self.raster_model.values():
            if cell.is_accessible:
                for herbivore, carnivore in zip(cell.herbivore_list, cell.carnivore_list):
                    if 0 <= herbivore.age < 5:
                        herbivore_0_5 += 1
                    elif 5 <= herbivore.age < 10:
                        herbivore_5_10 += 1
                    elif 10 <= herbivore.age < 15:
                        herbivore_10_15 += 1
                    elif herbivore.age <= 15:
                        herbivore_15plus += 1
                    if 0 <= carnivore.age < 5:
                        carnivore_0_5 += 1
                    elif 5 <= carnivore.age < 10:
                        carnivore_5_10 += 1
                    elif 10 <= carnivore.age < 15:
                        carnivore_10_15 += 1
                    elif carnivore.age <= 15:
                        carnivore_15plus += 1
        age_list = [[carnivore_0_5, -herbivore_0_5],[carnivore_5_10, -herbivore_5_10], [carnivore_10_15, -herbivore_10_15], [carnivore_15plus, -herbivore_15plus]]
        return age_list

    def biomass_food_chain(self):
        biomass_fodder = 0
        biomass_herbs = 0
        biomass_carnivores = 0
        for cell in self.raster_model.values():
            if cell.is_accessible:
                biomass_fodder += cell.fodder
                biomass_herbs += cell.biomass_herbivores()
                biomass_carnivores += cell.biomass_carnivores()
        biomass_list = {"biomass_fodder":biomass_fodder,
                        "biomass_herbs":biomass_herbs,
                        "biomass_carnivores": biomass_carnivores}
        return biomass_list

    # def population_pyramid(self, age_list):
        # df = pd.DataFrame(age_list, columns = ["Herbivores","Carnivores"], index =["0-5", "5-10", "10-5", "15+"])
        # df = df.rename_axis('Age').reset_index()
        # fig, ax = plt.subplots()
        # sns.barplot(x="Herbivores", y="Age", color="seagreen",
        #                    data=df,order=["15+", "10-5","5-10", "0-5"])
        # sns.barplot(x="Carnivores", y="Age", color="plum",
        #                    data=df, order=["15+", "10-5","5-10", "0-5"])
        #
        # plt.xlabel('Amount')
        # plt.xticks(np.arange(-800,801, step=200),(800,600, 400, 200, 0, 200, 400, 600, 800))
        # plt.text(0.2, -0.15, 'Carnivores', color='plum', transform= ax.transAxes)
        # plt.text(0.7, -0.15, 'Herbivores', color='seagreen', transform= ax.transAxes)
        # plt.title("Population Pyramid for Rossumøya")
        # ax.text(0.05, 0.95, "Year xxx", transform=ax.transAxes, fontsize=14,
        #         verticalalignment='top')
        # plt.show()

    # def stacked_area(self, biomass_list)
    #     df = pd.DataFrame(biomass_list)
    #     fig, ax = plt.subplots(1, 1, figsize=(16, 9), dpi=80)
    #     columns = df.columns[0:]
    #     x = [0,1] #year the simulation last
    #     y0 = df[columns[0]].values.tolist()
    #     y1 = df[columns[1]].values.tolist()
    #     y2 = df[columns[2]].values.tolist()
    #     y = np.vstack([y0, y1, y2])
    #     labs = columns.values.tolist()
    #     ax = plt.gca()
    #     ax.stackplot(x, y, labels=labs, colors=['tab:green', 'tab:purple', 'tab:red'])
    #     ax.set(ylim=[0, 100000])
    #     ax.legend(fontsize=10, ncol=4)
    #     plt.xticks(x[::5], fontsize=10, horizontalalignment='center')
    #     plt.yticks(np.arange(10000, 100000, 20000), fontsize=10)
    #     plt.xlim(x[0], x[-1])
    #     plt.show()


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

    island.populate_island([{'loc': (1, 18), 'pop': [{'species': 'Herbivore', 'age': 0, 'weight': None} for _ in range(100)]}])

    for x in range(30):
        island.annual_cycle()
        print("year", x)
        print("total ani", len(Animals.instances))
        print(len(island.raster_model[(1,18)].herbivore_list))
        print(island.raster_model[(1,18)].biomass_herbivores())
        print("############")

    island.populate_island([{'loc': (1, 17), 'pop': [{'species': 'Carnivore', 'age': 0, 'weight': 80} for _ in range(300)]}])


    for x in range(10):
        island.annual_cycle()
        print("year", x)
        print("total ani", len(Animals.instances))
        total_herb = 0
        total_carn = 0
        for cell in island.raster_model.values():
            if cell.is_accessible:
                total_carn += len(cell.carnivore_list)
                total_herb += len(cell.herbivore_list)
        print("total herbs:", total_herb)
        print("total carns:", total_carn)
        print(len(island.raster_model[(1, 18)].herbivore_list))
        print(island.raster_model[(1, 18)].biomass_herbivores())
        print("############")

    # island.pandas_dataframe()
    print(island.population_age_grups())
    # island.population_pyramid()
    print(island.biomass_food_chain())


