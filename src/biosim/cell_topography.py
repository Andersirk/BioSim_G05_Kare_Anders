# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import random
import src.animals.py as animals
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
        self.animals = []
        self.herbivore_list = []
        self.carnivore_list = []
        self.fodder = 0.0

    def decrease_fodder(self, decrease_amount):
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
        elif self.fodder <= 0.0:
            return 0.0

    def remove_animal(self, animal):
        """
        Removes the instance of an animal from the list of animal instances
        in the cell.
        :param animal: An instance of an animal class.
        """
        if animal.__class__.__name__ == "Herbivores":
            self.herbivore_list.remove(animal)
        elif animal.__class__.__name__ == "Carnivores":
            self.carnivore_list.remove(animal)


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
        """Returns the amount of fodder in the cell. """
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

    def breeding_herbivore(self):
        breedable_herbivores = len(self.herbivore_list)
        for herbivore in self.herbivore_list:
            breeding_prop = min(1, herbivore.parameters["gamma"] * herbivore.fitness * (breedable_herbivores - 1))
            if herbivore.weight < herbivore.parameters["zeta"]*(herbivore.parameters["w_birth"]+(herbivore.parameters["sigma_birth"])):
                continue
            if random.random() > breeding_prop:
                continue
            new_kid = animals.Herbivores()
            if herbivore.parameters["xi"]*new_kid.weight > herbivore.weight:
                continue
            herbivore.weight -= herbivore.parameters["xi"]*new_kid.weight
            self.add_animal(new_kid)

    def breeding_carnivore(self):
        breedable_carnivores = len(self.carnivore_list)
        for carnivore in self.carnivore_list:
            breeding_prop = min(1, carnivore.parameters["gamma"] * carnivore.fitness * (breedable_carnivores - 1))
            if carnivore.weight < carnivore.parameters["zeta"]*(carnivore.parameters["w_birth"]+(carnivore.parameters["sigma_birth"])):
                continue
            if random.random() > breeding_prop:
                continue
            new_kid = animals.Carnivore()
            if carnivore.parameters["xi"]*new_kid.weight > carnivore.weight:
                continue
            carnivore.weight -= carnivore.parameters["xi"]*new_kid.weight
            self.add_animal(new_kid)

    def death_herbivore(self):
        herbivore_reference_list = copy.copy(self.herbivore_list)
        for herbivore in herbivore_reference_list:
            if herbivore.fitness == 0:
                self.remove_animal(herbivore)
            elif random.random() > herbivore.weight*(1 - herbivore.fitness):
                self.remove_animal(herbivore)
            else:
                continue

    def feeding_herbivores(self):
        sorted_by_fitness = sorted(self.herbivore_list,
                                   key=lambda herbi: herbi.fitness)
        for herbivore in sorted_by_fitness:
            allowed_amount = self.decrease_fodder(herbivore.parameters["F"])
            herbivore.eat_fodder_increase_weight(allowed_amount)
            if self.fodder <= 0:
                break

    def feeding_carnivores(self):
        sorted_by_fitness = sorted(self.carnivore_list,
                                   key=lambda carni: carni.fitness)

class Jungle(Topography):

    parameters = {"f_max": 800}

    def __init__(self):
        """Constructor for the Jungle subclass, sets the inital fodder based
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
        """
        for parameter, value in new_parameters.items():
            if parameter == "f_max":
                if value >= 0:
                    cls.parameters["f_max"] = value
                else:
                    raise ValueError("f_max requires a positive value")
            else:
                raise ValueError(f"{parameter} is not an accepted parameter")

    def increase_fodder(self):
        """Increases the fodder for the Jungle cell"""
        self.fodder = self.f_max


class Savanna(Topography):
    """
    Construct the active subclass 'Savanna'.
    The fodder produced in this topography class has a lower growth rate than
    the jungle and is therefore vulnerable for overgrazing"
    """
    parameters = {"f_max": 300, "alpha": 0.3}

    def __init__(self):
        super().__init__()
        self.fodder = self.parameters["f_max"]

    @classmethod
    def set_parameters(cls, parameters):
        """ Sets the editable default parameters for this subclass"""
        for parameter, value in parameters.items():
            if parameter == "f_max":
                if value >= 0:
                    cls.parameters["f_max"] = value
                else:
                    raise ValueError("f_max requires a positive value")
            elif parameter == "alpha":
                if value >= 0:
                    cls.parameters["alpha"] = value
                else:
                    raise ValueError("alpha requires a positive value")
            else:
                raise ValueError(f"{parameter} is not an accepted parameter")

    def increase_fodder(self):
        """Sets the yearly fodder growth rate for this topography class"""
        self.fodder += self.parameters["alpha"] * (self.parameters["f_max"] - self.fodder)


class Desert(Topography):
    """
    Construct the active subclass 'Desert', which dosent allow the herbivore
    to feed due to the harsh climate. Movement and breeding for all
    animals is allowed.
    """
    def __init__(self):
        super().__init__()


class Mountain:
    """Construct the passive and non accessible class 'Mountain' """
    def __init__(self):
        self.is_accessible = False
        self.fodder = 0.0


class Ocean:
    """
    Construct the passive and non accessible class 'Ocean',
    witch surrounds the island
    """
    def __init__(self):
        self.is_accessible = False
        self.fodder = 0.0






# if __name__ == "__main__":
#
#
#     keke = [Savanna() for _ in range(5)]
#     [print(kok.parameters) for kok in keke]
#     Savanna.set_parameters({"f_max":2000, "alpha": 69})
#     [print(kok.parameters) for kok in keke]
