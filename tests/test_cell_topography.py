# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import src.biosim.cell_topography as topo


def test_test():
    ke=topo.Jungle()
    assert ke.fodder == 800


def test_current_occupants_int():
    instance = topo.Topography()
    assert type(instance.current_occupants()["Herbivores"]) == int and type(instance.current_occupants()["Carnivores"]) == int


def test_current_occupants_positive():
    instance = topo.Topography()
    assert instance.current_occupants()["Herbivores"] >= 0 and instance.current_occupants()["Carnivores"] >= 0


def test_animal_list():
    instance = topo.Topography()
    assert type(instance.animals) == list


def test_current_fodder():
    instance = topo.Topography()
    assert type(instance.current_fodder()) == int and instance.current_fodder() >= 0


def test_remove_animal():
    instance = topo.Topography()
    instance.animals = [1, 2, 3, 4]
    instance.remove_animal(4)
    assert instance.animals == [1, 2, 3]


def test_add_animal():
    instance = topo.Topography()
    instance.animals = [1, 2, 3, 4]
    instance.add_animal(5)
    assert instance.animals == [1, 2, 3, 4, 5]




