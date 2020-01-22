# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

from math import exp
import numpy as np
import random
import copy
import functools


class Animals:
    """The overall class for the animals which lives on the island"""
    instances = []
    parameters = {}

    @classmethod
    def age_up(cls):
        """
        Increases the age by one year of all animals alive.
        """
        for instance in cls.instances:
            instance.age += 1

    @classmethod
    def annual_metabolism(cls):
        """
        Decreases the animals weight based on the parameter 'eta'. The decrease
        amount is a factor of 'eta' times weight
        """
        for instance in cls.instances:
            instance.weight -= instance.parameters["eta"] * instance.weight

    @classmethod
    def reset_migration_attempt(cls):
        """
        Resets an animals migration attempts attribute
        """
        for instance in cls.instances:
            instance.has_tried_migration_this_year = False

    def __init__(self, age, weight, potential_newborn):
        """
        :param age: int, the age of an animal
        :param weight: float, the weight of an animal
        :param potential_newborn: boolean, if True the instance is not added
            to class instance list

        Constructor for the Animal class
        """
        self.age = age
        self.weight = self._birth_weight() if weight is None else weight
        if not potential_newborn:
            Animals.instances.append(self)
        self.has_tried_migration_this_year = False

    def _birth_weight(self):
        """
        :return: float, weight of a newborn

        Returns a weight drawn from a normal distribution with the
        parameter 'w_birth' as the expectation and 'sigma_birth' as the
        standard deviation
        """
        return random.normalvariate(
            self.parameters["w_birth"],
            self.parameters["sigma_birth"]
        )

    @property
    @functools.lru_cache(maxsize=256)
    def fitness(self):
        """
        :return: float: the fitness of the animal

        Computes the fitness of an animal based on the weight and age of the
        animal along with some species specific parameters. The animal has zero
        fitness if is has zero weight.
        """
        if self.weight <= 0:
            return 0
        else:
            return (1 + exp(
                self.parameters["phi_age"] * (
                        self.age - self.parameters["a_half"]))) ** -1 * (
                    1 + exp(-self.parameters["phi_weight"] * (
                        self.weight - self.parameters["w_half"]))) ** -1

    def _eat_increase_weight(self, food):
        """
        :param food: float: amount of food eaten

        Makes the animal eat x amount of food and increases its weight based on
        the parameter 'beta
        """
        self.weight += self.parameters["beta"] * food

    def breed(self, cell, cell_population):
        """
        :param cell: instance of the cell the animal is in
        :param cell_population: The amount of animals in the respective
            location of the same species

        Makes an animal try to breed.
        """
        breeding_probability = min(1, self.parameters["gamma"] *
                                   self.fitness * (cell_population - 1))
        if self.weight < self.parameters["zeta"] * \
                (self.parameters["w_birth"] +
                 (self.parameters["sigma_birth"])):
            return
        if random.random() > breeding_probability:
            return
        potential_newborn = self.__class__(potential_newborn=True)
        if self.parameters["xi"]*potential_newborn.weight > self.weight:
            return
        self.weight -= self.parameters["xi"]*potential_newborn.weight
        cell.add_animal(potential_newborn)
        Animals.instances.append(potential_newborn)

    def will_die_natural_death(self):
        """
        :return: boolean, True if an animal shall die or False if not

        Decides if an animal will die a 'natural' death based on a probability
        computed by the parameter 'omega' * (1 - fitness). If the animals
        fitness is 0 it dies with certain probability.
        """
        if self.fitness == 0 or random.random() <\
                self.parameters["omega"] * (1 - self.fitness):
            return True
        else:
            return False

    def _will_migrate(self):
        """
        :return: boolean, True if an animal shall try to migrate or False
            if not

        Decides if an animal shall try to migrate
        """
        probability_to_move = self.parameters["mu"] * self.fitness
        if random.random() < probability_to_move:
            return True
        else:
            return False

    def what_cell_to_migrate_to(self, current_cell, ek_dict):
        """
        :param current_cell: tuple, the animal's location cell at the start of
            the year
        :param ek_dict: dictionary with ek for all cells on the island
        :return: The chosen cell to migrate to

        Decides which of the neighbouring cell an animal shall to migrate to.
        based on it's current cell and the neighbouring cells abundance of
        fodder(ek)
        """
        self.has_tried_migration_this_year = True
        if self._will_migrate():
            sum_ek_neighbours = 0
            cell_probability = []
            neighbouring_cells = self._find_neighbouring_cells(current_cell)
            original_neighbouring_cells = copy.deepcopy(neighbouring_cells)
            for cell in original_neighbouring_cells:
                if cell not in ek_dict.keys():
                    neighbouring_cells.remove(cell)
                else:
                    sum_ek_neighbours += ek_dict[cell]
            if sum_ek_neighbours == 0 or len(neighbouring_cells) == 0:
                return current_cell
            for cell in neighbouring_cells:
                cell_probability.append(ek_dict[cell] / sum_ek_neighbours)
            cumulative_probability = np.cumsum(cell_probability)
            random_number = random.random()
            n = 0
            while random_number >= cumulative_probability[n]:
                n += 1
            return neighbouring_cells[n]
        return current_cell

    @staticmethod
    def _find_neighbouring_cells(coordinates):
        """
        :param coordinates: list with tuples (coordinates)
        :return: a list with an animals neighbouring cell coordinates

        Finds an animals neighbouring cell coordinates
        """
        neighbouring_cells = [(coordinates[0]+1, coordinates[1]),
                              (coordinates[0]-1, coordinates[1]),
                              (coordinates[0], coordinates[1]+1),
                              (coordinates[0], coordinates[1]-1)]
        return neighbouring_cells


class Herbivores(Animals):
    """
    The class for the plant eating herbivores which lives on the island
    """
    parameters = {"w_birth": 8.0,
                  "sigma_birth": 1.5,
                  "beta": 0.9,
                  "eta": 0.05,
                  "a_half": 40.0,
                  "phi_age": 0.2,
                  "w_half": 10,
                  "phi_weight": 0.1,
                  "mu": 0.25,
                  "lambda": 1.0,
                  "gamma": 0.2,
                  "zeta": 3.5,
                  "xi": 1.2,
                  "omega": 0.4,
                  "F": 10,
                  "DeltaPhiMax": None
                  }

    def __init__(self, age=0, weight=None, potential_newborn=False):
        """
        :param age: int, the age of an herbivore
        :param weight: float, the weight of an herbivore
        :param potential_newborn: boolean, if True the instance is not added
            to class instance list

        Constructor for the Herbivore subclass. If weight is set to None
        the weight will be drawn from a gaussian distribution, with 'w_birth'
        as the expectation and 'sigma_birth' as the standard deviation.
        """
        super().__init__(age, weight, potential_newborn)

    def graze(self, cell):
        """
        :param cell: instance of the cell the animal is in

        A method which makes the herbivore attempt to graze, dependent on
        the remaining amount of fodder in it's respective cell.
        """
        allowed_amount = cell.allowed_fodder_to_consume(self.parameters["F"])
        self._eat_increase_weight(allowed_amount)

    @classmethod
    def set_parameters(cls, new_parameters):
        """
        :param new_parameters: A dictionary with keys as the parameter to
            be changed and values as the new parameter value. It is possible to
            change preexisting parameters only.

        Sets the parameters of all herbivore instances to the provided
        new_parameters.
        """
        for parameter, value in new_parameters.items():
            if parameter in cls.parameters.keys():
                if value < 0:
                    raise ValueError(
                        f"{parameter} value must be positive")
                if parameter == "DeltaPhiMax" and value <= 0:
                    raise ValueError(
                        f"{parameter} value must be strictly positive")
                if parameter == "eta" and value > 1:
                    raise ValueError(
                        f"{parameter} value must be 0, 1 or in between")
                cls.parameters[parameter] = value
            else:
                raise ValueError(f"{parameter} is not an accepted parameter")


class Carnivores(Animals):
    """
    This is the class for the meat eating carnivores which lives on
    the island
    """
    parameters = {"w_birth": 6.0,
                  "sigma_birth": 1.0,
                  "beta": 0.75,
                  "eta": 0.125,
                  "a_half": 60.0,
                  "phi_age": 0.4,
                  "w_half": 4,
                  "phi_weight": 0.4,
                  "mu": 0.4,
                  "lambda": 1.0,
                  "gamma": 0.8,
                  "zeta": 3.5,
                  "xi": 1.1,
                  "omega": 0.9,
                  "F": 50,
                  "DeltaPhiMax": 10}

    def __init__(self, age=0, weight=None, potential_newborn=False):
        """
        :param age: int, the age of an animal
        :param weight: float, the weight of an animal
        :param potential_newborn: boolean, if True the instance is not added
            to class instance list

        Constructor for the Carnivore subclass. If weight is set to None
        the weight will be drawn from a gaussian distribution, with 'w_birth'
        as the expectation and 'sigma_birth' as the standard deviation.
        """
        super().__init__(age, weight, potential_newborn)
        self.eaten_this_year = 0

    def kills_herbivore(self, herbivore):
        """
        :param herbivore: The herbivore the carnivore will attempt to kill
        :return: boolean, True if the killing was successful, False if not

        This function makes the carnivores try to kill and eat a herbivore
        """
        if self.fitness < herbivore.fitness or self.eaten_this_year >= \
                self.parameters["F"]:
            return False
        elif (self.fitness - herbivore.fitness) <\
                self.parameters["DeltaPhiMax"]:
            killing_prop = (self.fitness - herbivore.fitness) / \
                           self.parameters["DeltaPhiMax"]
            if random.random() < killing_prop:
                self.eaten_this_year += herbivore.weight
                self._eat_increase_weight(herbivore.weight)
                return True
            else:
                return False
        else:
            self.eaten_this_year += herbivore.weight
            self._eat_increase_weight(herbivore.weight)
            return True

    def reset_amount_eaten_this_year(self):
        """
        Resets the amount of food a carnivore has eaten for one year
        """
        self.eaten_this_year = 0

    @classmethod
    def set_parameters(cls, new_parameters):
        """
        :param new_parameters: A dictionary with keys as the parameter to
            be changed and values as the new parameter value. It is possible to
            change preexisting parameters only.

        Sets the parameters of all carnivore instances to the provided
        new_parameters.
        """
        for parameter, value in new_parameters.items():
            if parameter in cls.parameters.keys():
                if value < 0:
                    raise ValueError(f"{parameter} value must be positive")
                if parameter == "DeltaPhiMax" and value <= 0:
                    raise ValueError(
                        f"{parameter} value must be strictly positive")
                if parameter == "eta" and value > 1:
                    raise ValueError(
                        "{parameter} value must be 0, 1 or in between")
                cls.parameters[parameter] = value
            else:
                raise ValueError(f"{parameter} is not an accepted parameter")
