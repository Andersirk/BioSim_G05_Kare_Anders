# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"


class Topography:
    def __init__(self):
        self.accessible = True
        self.animals = []
        self.fodder = 0

    def decrease_fodder(self, decrease_amount):
        if decrease_amount <= self.fodder:
            self.fodder -= decrease_amount
            return decrease_amount
        elif decrease_amount > self.fodder:
            remaining_fodder = self.fodder
            self.fodder = 0
            return remaining_fodder
        elif self.fodder <= 0:
            return 0

    def remove_animal(self, animal):
        self.animals.remove(animal)

    def add_animal(self, animal):
        self.animals.append(animal)

    def current_fodder(self):
        return self.fodder

    def current_occupants(self):
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
        super().__init__()
        self.fodder = self.parameters["f_max"]

    @classmethod
    def set_parameters(cls, new_parameters):
        for parameter, value in new_parameters.items():
            if parameter == "f_max":
                if value >= 0:
                    cls.parameters["f_max"] = value
                else:
                    raise ValueError("f_max requires a positive value")
            else:
                raise ValueError(f"{parameter} is not an accepted parameter")

    def increase_fodder(self):
        """Increases """
        self.fodder = self.f_max


class Savanna(Topography):
    parameters = {"f_max": 300, "alpha": 0.3}

    def __init__(self):
        super().__init__()
        self.fodder = self.parameters["f_max"]

    @classmethod
    def set_parameters(cls, parameters):
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
        self.fodder += self.parameters["alpha"] * (self.parameters["f_max"] - self.fodder)



class Desert(Topography):
    def __init__(self):
        super().__init__()


class Mountain:
    def __init__(self):
        self.accessible = False
        self.fodder = 0


class Ocean:
    def __init__(self):
        self.accessible = False
        self.fodder = 0






if __name__ == "__main__":


    keke = [Savanna() for _ in range(5)]
    [print(kok.parameters) for kok in keke]
    Savanna.set_parameters({"f_max":2000, "alpha": 69})
    [print(kok.parameters) for kok in keke]
