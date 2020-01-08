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
    def __init__(self):
        super().__init__()
        self.f_max_jungle = 800.0
        self.fodder = self.f_max_jungle

    def set_attributes(self):
        pass

    def increase_fodder(self):
        """Increases """
        self.fodder = self.f_max_jungle

class Savanna(Topography):
    def __init__(self):
        super().__init__()
        self.f_max_savanna = 300.0
        self.alpha = 0.3
        self.fodder = self.f_max_savanna

    def set_attributes(self):
        pass

    def increase_fodder(self):
        self.fodder += self.alpha * (self.f_max_savanna - self.fodder)



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


def create_map(island_map):
    """ Creates a dictionary where the keys are coordinates and values
    are a class with the relevant topography category.

    :param island_map:
    :return dictinary,
    """
    island_map_no_spaces = island_map.replace(" ", "")
    x, y = 0, -1
    raster_model = {}
    for number, landscape_code in enumerate(island_map_no_spaces):
        y += 1
        if landscape_code == "D":
            raster_model[(x, y)] = Desert()
        elif landscape_code == "J":
            raster_model[(x, y)] = Jungle()
        elif landscape_code == "S":
            raster_model[(x, y)] = Savanna()
        elif landscape_code == "O":
            raster_model[(x, y)] = Ocean()
        elif landscape_code == "M":
            raster_model[(x, y)] = Mountain()
        elif landscape_code == "\n":
            y = -1
            x += 1
        if x == 0 and landscape_code != "O":
            raise ValueError
        elif y == 0 and landscape_code != "O":
            raise ValueError
        if landscape_code not in ["O", "M", "J", "S", "D", "\n"]:
            raise ValueError
    return raster_model



if __name__ == "__main__":
    geogr = """\
                OOOOOOOOOOOOOOOOOOOOO
                OOOOOOOOSMMMMJJJJJJJO
                OSSSSSJJJJMMJJJJJJJOO
                OSSSSSSSSSMMJJJJJJOOO
                OSSSSSJJJJJJJJJJJJOOO
                OSSSSSJJJDDJJJSJJJOOO
                OSSJJJJJDDDJJJSSSSOOO
                OOSSSSJJJDDJJJSOOOOOO
                OSSSJJJJJDDJJJJJJJOOO
                OSSSSJJJJDDJJJJOOOOOO
                OOSSSSJJJJJJJJOOOOOOO
                OOOSSSSJJJJJJJOOOOOOO
                OOOOOOOOOOOOOOOOOOOOO"""


    mappp = create_map(geogr)
    for key, value in mappp.items():
        if value.__class__.__name__ != "Ocean" and value.__class__.__name__ != "Mountain":
            print (f'Coordinate: {key}, has {value.fodder} fodder and the geography is {value.__class__.__name__}, {value.current_occupants()}')
