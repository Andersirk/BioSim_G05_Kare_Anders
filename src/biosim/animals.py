# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

from math import exp
import numpy as np


class Animals:
    instances = []
    """This is the overall class for the animals which lives on the island"""

    def __init__(self, age=0):
        self.age = age
        self.weight = self.birth_weight()
        self.fitness = 0
        self.fitness_update()

    def birth_weight(self):
        return np.random.normal(
            self.parameters["w_birth"],
            self.parameters["sigma_birth"]
        )

    def fitness_update(self):
        if self.weight <= 0:
            self.weight = 0
        else:
            self.fitness = (1 + exp(self.parameters["phi_age"] * (self.age - self.parameters["a_half"])))** -1 * (
                    1 + exp(-self.self.parameters["phi_weight"] *(self.weight - self.parameters["w_half"])))** -1


    @classmethod
    def fitness_update_all(cls):
        """This function calculates the instances fitness condition """
        for instance in cls.instances:
            instance.fitness_update()


    def migration(self):
        """This function decides if, and to which cell, an animal shall move"""


    def breeding(self):
        """This function decides if an animal will breed"""


    def death(self):
        """This function decides if an animal will die"""


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


    def __init__(self):
        pass

    def eat(self):
        """This function makes the herbivores try to eat """
        pass


class Herbivores(Animals):
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

    def __init__(self):
        pass

    def eat(self):
        """This function makes the carnivores try to eat """
        pass



