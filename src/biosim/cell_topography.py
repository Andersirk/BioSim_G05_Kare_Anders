# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"


class Topography:
    """
    Topography superclass from where all active cell-types are subclassed.
    Represents a single cell on the map
    """
    def __init__(self):
        """
        Topography superclass constructor
        """
        self.accessible = True
        self.animals = []
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
        self.animals.remove(animal)

    def add_animal(self, animal):
        """
        Adds the instance of an animal to the list of animal instances
        in the cell.
        :param animal: An instance of an animal class.
        """
        self.animals.append(animal)

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
        herbivore_count = 0
        carnivore_count = 0
        for animal in self.animals:
            if animal.__class__.__name__ == "Herbivore":
                herbivore_count += 1
            elif animal.__class__.__name__ == "Carnivore":
                carnivore_count += 1
        return {"Herbivores": herbivore_count,
                "Carnivores": carnivore_count,
                "Total": len(self.animals)}



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
        self.accessible = False
        self.fodder = 0.0


class Ocean:
    """
    Construct the passive and non accessible class 'Ocean',
    witch surrounds the island
    """
    def __init__(self):
        self.accessible = False
        self.fodder = 0.0






if __name__ == "__main__":


    keke = [Savanna() for _ in range(5)]
    [print(kok.parameters) for kok in keke]
    Savanna.set_parameters({"f_max":2000, "alpha": 69})
    [print(kok.parameters) for kok in keke]
