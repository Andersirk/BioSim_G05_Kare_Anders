# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

from math import exp
import numpy as np
import random
import biosim.cell_topography as topo
import copy
import functools


class Animals:
    instances = []
    """This is the overall class for the animals which lives on the island"""
    def __init__(self, age, weight, potential_newborn):
        self.age = age
        self.weight = self.birth_weight() if weight is None else weight
        if not potential_newborn:
            Animals.instances.append(self)
            #newborns blir lagt til selvom de blir skrapa
        self.has_tried_migration_this_year = False

    def birth_weight(self):
        """
        Returns a weight drawn from a normal distribution with the
        parameter 'w_birth' as the expectation and 'sigma_birth' as the
        standard deviation
        :return: float :weight of a newborn
        """
        return random.normalvariate(
            self.parameters["w_birth"],
            self.parameters["sigma_birth"]
        )

    @property
    @functools.lru_cache(maxsize=256)
    def fitness(self):
        """
        Computes the fitness of an animal based on the weight and age of the
        animal along with some species specific parameters. The animal has zero
        fitness if is has zero weight.

        :return: float: the fitness of the animal
        """
        if self.weight <= 0:
            return 0
        else:
            return (1 + exp(
                self.parameters["phi_age"] * (
                        self.age - self.parameters["a_half"])))** -1 * (
                    1 + exp(
                -self.parameters["phi_weight"] *(
                        self.weight - self.parameters["w_half"]))) ** -1

    @classmethod
    def age_up(cls):
        """
        Increases the age by one year of all animals alive.
        :return: None
        """
        for instance in cls.instances:
            instance.age += 1

    @classmethod
    def annual_metabolism(cls):
        """
        Decreases the animals weight based on the parameter 'eta'
        :return: None
        """
        for instance in cls.instances:
            instance.weight -= instance.parameters["eta"] * instance.weight

    def eat_increase_weight(self, food):
        """
        Makes the animal eat x amount of food and increases its weight based on
        the parameter 'beta
        :param food: float: amount of food eaten
        :return: None
        """
        self.weight += self.parameters["beta"] * food

    def breed(self, cell, cell_population):
        """
        Makes an animal try to breed
        :param cell: The animals location cell at the start of the year
        :param cell_population: The amount of animals in the respective
        population
        :return: None
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
        Decides if an animal will die a 'natural' death
        :return: True or False
        """
        if self.fitness == 0 or random.random() <\
                self.parameters["omega"] * (1 - self.fitness):
            return True
        else:
            return False

    def will_migrate(self):
        """
        Decides if an animal shall try to migrate
        :return:True (shall try to migrate) or False (Shall not try to migrate)
        """
        probability_to_move = self.parameters["mu"] * self.fitness
        if random.random() < probability_to_move:
            return True
        else:
            return False

    def what_cell_to_migrate_to(self, current_cell, ek_dict):
        """
        Decides which of the neighbouring cell an animal shall to migrate to.
        :param current_cell: The animals location cell at the start of the year
        :param ek_dict: Dictionary with the neighbouring cells
        coordinates (key) and the respective cells relevant ek.
        :return: The chosen target for the migration and the current cell
        """
        self.has_tried_migration_this_year = True
        if self.will_migrate():
            sum_ek_neighbours = 0
            cell_probability = []
            neighbouring_cells = self.find_neighbouring_cells(current_cell)
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

    def find_neighbouring_cells(self, coordinates):
        """
        Finds an animals neighbouring cell coordinates
        :param coordinates: list
        :return: a list with an animals neighbouring cell coordinates
        """
        neighbouring_cells = [(coordinates[0]+1, coordinates[1]),
                              (coordinates[0]-1, coordinates[1]),
                              (coordinates[0], coordinates[1]+1),
                              (coordinates[0], coordinates[1]-1)]
        return neighbouring_cells

    @classmethod
    def reset_migration_attempt(cls):
        for instance in cls.instances:
            instance.has_tried_migration_this_year = False


class Herbivores(Animals):
    """
    This is the class for the plant eating herbivores which lives on
    the island
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
        super().__init__(age, weight, potential_newborn)

    def graze(self, cell):
        """
        A method which makes the herbivore graze
        :param cell: The animals location cell at the start of the year
        :return: None
        """
        allowed_amount = cell.allowed_fodder_to_consume(self.parameters["F"])
        self.eat_increase_weight(allowed_amount)

    @classmethod
    def set_parameters(cls, new_parameters):
        """
        Sets the parameters of all herbivore instances to the provided
        new_parameters.
        :param new_parameters: A dictionary with keys as the parameter to
        be changed and values as the new parameter value. It is possible to
        change preexisting parameters only.
        :return: None
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
        super().__init__(age, weight, potential_newborn)
        self.eaten_this_year = 0

    def kills_herbivore(self, herbivore):
        """
        This function makes the carnivores try to kill and eat a herbivore
        :param herbivore: instance in the herbivore subclass
        :return: True (if the killing was successful) or False if it failed
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
                self.eat_increase_weight(herbivore.weight)
                return True
            else:
                return False
        else:
            self.eaten_this_year += herbivore.weight
            self.eat_increase_weight(herbivore.weight)
            return True

    def reset_amount_eaten_this_year(self):
        """
        Resets the amount of food a carnivore has eaten for one year
        :return:None
        """
        self.eaten_this_year = 0

    @classmethod
    def set_parameters(cls, new_parameters):
        """
        Sets the parameters of all carnivore instances to the provided
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
                if parameter == "DeltaPhiMax" and value <= 0:
                    raise ValueError(
                        f"{parameter} value must be strictly positive")
                if parameter == "eta" and value > 1:
                    raise ValueError(
                        "{parameter} value must be 0, 1 or in between")
                cls.parameters[parameter] = value
            else:
                raise ValueError(f"{parameter} is not an accepted parameter")

