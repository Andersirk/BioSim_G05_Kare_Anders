# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

from math import exp
import numpy as np
import random


class Animals:
    instances = []
    """This is the overall class for the animals which lives on the island"""

    def __init__(self, age=0, weight=None):
        self.age = age
        self.weight = self.birth_weight() if weight is None else weight
        Animals.instances.append(self)

    def birth_weight(self):
        return np.random.normal(
            self.parameters["w_birth"],
            self.parameters["sigma_birth"]
        )

    @property
    def fitness(self):
        if self.weight <= 0:
            return 0
        else:
            return (1 + exp(
                self.parameters["phi_age"] * (
                        self.age - self.parameters["a_half"])))** -1 * (
                    1 + exp(
                -self.parameters["phi_weight"] *(
                        self.weight - self.parameters["w_half"]))) ** -1


    def breeding(self):
        """This function decides if an animal will breed"""



    def death(self):
        """This function decides if an animal will die"""

    def will_migrate(self):
        """This function decides if, and to which cell, an animal shall move"""
        probability_to_move = self.parameters["mu"] * self.fitness
        if random.random() < probability_to_move:
            return True
        else:
            return False


    @classmethod
    def age_up(cls):
        for instance in cls.instances:
            instance.age += 1

    @classmethod
    def weight_decrease(cls):
        """This function makes the animal lose weight"""
        for instance in cls.instances:
            instance.weight = instance.parameters["eta"] * instance.weight


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

    def __init__(self, age = 0, weight = None):
        super().__init__(age = 0, weight = None)

    def eat(self):
        """This function makes the herbivores try to eat """
        pass








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

    def __init__(self, age = 0, weight = None):
        super().__init__(age = 0, weight = None)

    def eat(self):
        """This function makes the carnivores try to eat """
        pass

    def migration(self):
        """This function decides if, and to which cell, an animal shall move"""


if __name__ == "__main__":
    print(Herbivores().__class__.__name__)
