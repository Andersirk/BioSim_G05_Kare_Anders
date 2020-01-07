# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"


class Topography:
    def __init__(self):
        self.accessible = False
        self.animals = []
        self.fodder = None

    def increase_fodder(self):
        """Increases """
        pass

    def decrease_fodder(self, decrease_amount):
        pass

    def remove_animal(self):
        pass

    def add_animal(self):
        pass

    def current_fodder(self):
        pass


class Jungle(Topography):
    def __init__(self):
        super().__init__()
        self.accessible = True

    def set_attributes(self):
        pass


class Savanna(Topography):
    def __init__(self):
        super().__init__()
        self.accessible = True

    def set_attributes(self):
        pass


class Desert(Topography):
    def __init__(self):
        super().__init__()
        self.accessible = True



