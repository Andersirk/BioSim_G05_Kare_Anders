# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import biosim.animals as animals
import copy


class Topography:
    """
    Topography superclass from where all active cell-types are subclassed.
    Represents a single cell on the map
    """
    def __init__(self):
        """
        Topography superclass constructor
        """
        self.is_accessible = True
        self.herbivore_list = []
        self.carnivore_list = []
        self.fodder = 0.0

    def allowed_fodder_to_consume(self, decrease_amount):
        """
        Takes a request for how much fodder the animal would like to consume
        and returns the amount it is allowed to consume and decreases the
        the fodder in the cell by the same amount.
        :param decrease_amount: The animals desired amount of fodder.
        :return: The allowed amount of fodder.
        """
        if decrease_amount <= self.fodder:
            self.fodder -= decrease_amount
            return decrease_amount
        elif decrease_amount > self.fodder:
            remaining_fodder = self.fodder
            self.fodder = 0.0
            return remaining_fodder

    def remove_animal(self, animal):
        """
        Removes the instance of an animal from the list of animal instances
        in the cell.
        :param animal: An instance of an animal class.
        """
        if animal.__class__.__name__ == "Herbivores":
            self.herbivore_list = [herbi for herbi in self.herbivore_list
                                   if animal != herbi]
        elif animal.__class__.__name__ == "Carnivores":
            self.carnivore_list = [carni for carni in self.carnivore_list
                                   if animal != carni]

    def add_animal(self, animal):
        """
        Adds the instance of an animal to the list of animal instances
        in the cell.
        :param animal: An instance of an animal class.
        """
        if animal.__class__.__name__ == "Herbivores":
            self.herbivore_list.append(animal)
        elif animal.__class__.__name__ == "Carnivores":
            self.carnivore_list.append(animal)

    def current_fodder(self):
        """
        Finds the current amount of fodder in a cell
        :return: A float
        """
        return self.fodder

    def current_occupants(self):
        """
        Counts the animals in the list of animals and returns a dictionary
        with the amount of Herbivores, Carnivores and the total of both.
        :return: A dictionary with Herbivores, Carnivores and total as keys,
                 and their population in the cell as values.
        """

        return {"Herbivores": len(self.herbivore_list),
                "Carnivores": len(self.carnivore_list),
                "Total": len(self.carnivore_list) + len(self.herbivore_list)}

    def breed_all_animals_in_cell(self):
        """
        Makes all animals in a cell breed
        :return: None
        """
        self.breed_all_herbivores_in_cell()
        self.breed_all_carnivores_in_cell()

    def breed_all_herbivores_in_cell(self):
        """
        Makes all herbivore in a cell breed
        :return: None
        """
        number_of_herbivores = len(self.herbivore_list)
        herbivore_reference_list = copy.copy(self.herbivore_list)
        for herbivore in herbivore_reference_list:
            herbivore.breed(self, number_of_herbivores)

    def breed_all_carnivores_in_cell(self):
        """
        Makes all herbivore in a cell breed
        :return: None
        """
        number_of_carnivores = len(self.carnivore_list)
        carnivore_reference_list = copy.copy(self.carnivore_list)
        for carnivore in carnivore_reference_list:
            carnivore.breed(self, number_of_carnivores)

    def natural_death_all_animals_in_cell(self):
        """
        All animals which will die a natual death in a cell are removed  
        :return: None
        """
        self.natural_death_all_herbivores_in_cell()
        self.natural_death_all_carnivores_in_cell()

    def natural_death_all_carnivores_in_cell(self):
        """
        All herbivores which will die a natual death  in a cell are removed
        :return: None
        """
        carnivores_reference_list = copy.copy(self.carnivore_list)
        for carnivore in carnivores_reference_list:
            if carnivore.will_die_natural_death():
                self.remove_animal(carnivore)
                animals.Animals.instances.remove(carnivore)

    def natural_death_all_herbivores_in_cell(self):
        """
        All carnivores for which will die natual death in a cell are removed
        :return: None
        """
        herbivores_reference_list = copy.copy(self.herbivore_list)
        for herbivore in herbivores_reference_list:
            if herbivore.will_die_natural_death():
                self.remove_animal(herbivore)
                animals.Animals.instances.remove(herbivore)

    def biomass_herbivores(self):
        """
        Calculates the biomass to all the herbivores in a cell
        :return: int
        """
        weight_sum = 0
        for herbivore in self.herbivore_list:
            weight_sum += herbivore.weight
        return weight_sum

    def biomass_carnivores(self):
        """
        Calculates the biomass to all the carnivores in a cell
        :return: int
        """
        weight_sum = 0
        for carnivore in self.carnivore_list:
            weight_sum += carnivore.weight
        return weight_sum

    def feed_herbivores_in_cell(self):
        """
        Makes all the herbivores in a cell try to graze
        :return: None
        """
        herbivore_fitness_sort = sorted(
            self.herbivore_list, key=lambda herbi: herbi.fitness, reverse=True)
        for herbivore in herbivore_fitness_sort:
            if self.fodder <= 0:
                break
            herbivore.graze(self)

    def feed_carnivores_in_cell(self):
        """
        Makes all the carnivore in a cell try to kill a herbivore. First the
        most fit carnivore tries to kill the least fit herbivore and so on,
        until it have reached it yearly eat-limit. Then its the second fittest
        carnivores turn, etc.
        :return: None
        """
        herbivore_fitness_sort = sorted(
            self.herbivore_list, key=lambda herbi: herbi.fitness)
        carnivore_fitness_sort = sorted(
            self.carnivore_list, key=lambda carni: carni.fitness, reverse=True)
        for carnivore in carnivore_fitness_sort:
            for herbivore in herbivore_fitness_sort:
                if carnivore.kills_herbivore(herbivore):
                    herbivore_fitness_sort.remove(herbivore)
                    self.remove_animal(herbivore)
                    animals.Animals.instances.remove(herbivore)
            carnivore.reset_amount_eaten_this_year()

    def ek_for_cell(self, species):
        """
        Calculates the relative amount of relevant fodder (ek) for the
        carnivores and the herbivores.
        :param species: Carnivores or Herbivores
        :return: herbivore_ek or carnivore_ek as floats.
        """
        if species == "Carnivores":
            return self.biomass_herbivores() / (
                        (len(self.carnivore_list) + 1
                         ) * animals.Carnivores.parameters["F"])
        elif species == "Herbivores":
            return self.current_fodder() / (
                        (len(self.herbivore_list) + 1
                         ) * animals.Herbivores.parameters["F"])

    def _migrate_all_herbivores_in_cell(self, island, current_cell,
                                        herbivore_ek):
        """
        Migrate all the herbivores which dosent already have tried to migrate
        this year.
        :param island: Class
        :param current_cell: tuple, the location (x,y) of the animal
        :param herbivore_ek: Int
        :return: None
        """
        for herbivore in self.herbivore_list:
            if not herbivore.has_tried_migration_this_year:
                new_location = herbivore.what_cell_to_migrate_to(current_cell,
                                                                 herbivore_ek)
                if new_location != current_cell:
                    self.remove_animal(herbivore)
                    island.raster_model[new_location].add_animal(herbivore)

    def _migrate_all_carnivores_in_cell(self, island, current_cell,
                                        carnivore_ek):
        """
        Migrate all the carnivores which dosent already have tried to migrate
        this year.
        :param island: Class
        :param current_cell: tuple, the location (x,y) of the animal
        :param carnivore_ek: Int
        :return: None
        """
        for carnivore in self.carnivore_list:
            if not carnivore.has_tried_migration_this_year:
                new_location = carnivore.what_cell_to_migrate_to(current_cell,
                                                                 carnivore_ek)
                if new_location != current_cell:
                    self.remove_animal(carnivore)
                    island.raster_model[new_location].add_animal(carnivore)

    def migrate_all_animals_in_cell(self, island, current_cell, carnivore_ek,
                                    herbivore_ek):
        """
        Migrate all the animals which dosent already have tried to migrate
        this year.
        :param island: Class
        :param current_cell: tuple, the location (x,y) of the animal
        :param carnivore_ek: Int
        :param herbivore_ek: Int
        :return: None
        """
        self._migrate_all_herbivores_in_cell(island, current_cell,
                                             herbivore_ek)
        self._migrate_all_carnivores_in_cell(island, current_cell,
                                             carnivore_ek)


class Jungle(Topography):
    """
    Construct the active subclass Jungle, where the primary production are
    large enough to restore it amount of foder to f_max each year.
    """
    parameters = {"f_max": 800}

    def __init__(self):
        """Constructor for the Jungle subclass, sets the initial fodder based
        on the initial value of f_max"""
        super().__init__()
        self.fodder = self.parameters["f_max"]

    @classmethod
    def set_parameters(cls, new_parameters):
        """
        Sets the parameters of all Jungle instances to the provided
        new_parameters.
        :param new_parameters: A dictionary with keys as the parameter to
        be changed and values as the new parameter value. It is possible to
        change preexisting parameters only.
        :return: None
        """
        for parameter, value in new_parameters.items():
            if parameter in cls.parameters.keys():
                if value < 0:
                    raise ValueError(f"{parameter} value must be positive")
                cls.parameters[parameter] = value
            else:
                raise ValueError(f"{parameter} is not an accepted parameter")

    def increase_fodder(self):
        """
        Increases the fodder for the Jungle cell
        :return: None
        """
        self.fodder = self.parameters["f_max"]


class Savanna(Topography):
    """
    Construct the active subclass 'Savanna'.
    The fodder produced in this topography class has a lower growth rate than
    the jungle and is therefore vulnerable for overgrazing"
    """
    parameters = {"f_max": 300, "alpha": 0.3}

    def __init__(self):
        """Constructor for the Savanna subclass, sets the initial fodder based
        on the initial value of f_max"""
        super().__init__()
        self.fodder = self.parameters["f_max"]

    @classmethod
    def set_parameters(cls, new_parameters):
        """
        Sets the parameters of all Savanna instances to the provided
        new_parameters.
        :param new_parameters: A dictionary with keys as the parameter to
        be changed and values as the new parameter value. It is possible to
        change preexisting parameters only.
        :return: None
        """
        for parameter, value in new_parameters.items():
            if parameter in cls.parameters.keys():
                if value < 0:
                    raise ValueError(f"{parameter} value must be positive")
                cls.parameters[parameter] = value
            else:
                raise ValueError(f"{parameter} is not an accepted parameter")

    def increase_fodder(self):
        """
        Sets the yearly fodder growth rate for Savanna topography class
        :return: None
        """
        self.fodder += self.parameters["alpha"] * (self.parameters["f_max"]
                                                   - self.fodder)


class Desert(Topography):
    """
    Construct the active subclass 'Desert', where the primary production = 0.
    Movement and breeding for all animals is allowed.
    :return: None
    """
    def __init__(self):
        super().__init__()
        self.fodder = 0


class Mountain:
    """Construct the passive and non accessible class 'Mountain'
    :return: None
    """
    def __init__(self):
        self.is_accessible = False


class Ocean:
    """
    Construct the passive and non accessible class 'Ocean',
    witch surrounds the island
    :return: None
    """
    def __init__(self):
        self.is_accessible = False
