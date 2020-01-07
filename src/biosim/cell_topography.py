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


class Mountain:
    def __init__(self):
        self.accessible = False


class Ocean:
    def __init__(self):
        self.accessible = False


def create_map(island_map):
     """ Creates a dictionary where the keys are coordinates and values
     are a class with the relevant topography category.

     :param island_map:
     :return dictinary,
     """
    island_map_no_spaces = island_map.replace(" ", "")
    x, y = 0, -1
    map = {}
    for number, landscape_code in enumerate(island_map_no_spaces):
        y += 1
        if landscape_code == "D":
            map[(x, y)] = Desert()
        elif landscape_code == "J":
            map[(x, y)] = Jungle()
        elif landscape_code == "S":
            map[(x, y)] = Savanna()
        elif landscape_code == "O":
            map[(x, y)] = Ocean()
        elif landscape_code == "M":
            map[(x, y)] = Mountain()
        elif landscape_code == "\n":
            y = -1
            x += 1
        if x == 0 and landscape_code != "O":
            raise ValueError
        elif y == 0 and landscape_code != "O":
            raise ValueError
        if landscape_code not in ["O", "M", "J", "S", "D"]:
            raise ValueError
    return map
