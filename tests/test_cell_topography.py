# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import src.biosim.cell_topography as topo


def test_Topo_decrease_fodder_abundance():
    instance = topo.Topography()
    instance.fodder = 400
    decrease_amount = instance.decrease_fodder(200)
    assert decrease_amount == 200
    assert instance.current_fodder() == 200


def test_Topo_decrease_fodder_scarce():
    instance = topo.Topography()
    instance.fodder = 100
    decrease_amount = instance.decrease_fodder(200)
    assert decrease_amount == 100
    assert instance.current_fodder() == 0


def test_Topo_decrease_fodder_zero():
    instance = topo.Topography()
    instance.fodder = 0
    decrease_amount = instance.decrease_fodder(200)
    assert decrease_amount == 0
    assert instance.current_fodder() == 0
    

def test_Topo_current_occupants_int():
    instance = topo.Topography()
    assert type(instance.current_occupants()["Herbivores"]) == int and type(instance.current_occupants()["Carnivores"]) == int


def test_Topo_current_occupants_positive():
    instance = topo.Topography()
    assert instance.current_occupants()["Herbivores"] >= 0 and instance.current_occupants()["Carnivores"] >= 0


def test_Topo_animal_list():
    instance = topo.Topography()
    assert type(instance.animals) == list


def test_Topo_current_fodder():
    instance = topo.Topography()
    assert type(instance.current_fodder()) == float and instance.current_fodder() >= float


def test_Topo_remove_animal():
    instance = topo.Topography()
    instance.animals = [1, 2, 3, 4]
    instance.remove_animal(4)
    assert instance.animals == [1, 2, 3]


def test_Topo_add_animal():
    instance = topo.Topography()
    instance.animals = [1, 2, 3, 4]
    instance.add_animal(5)
    assert instance.animals == [1, 2, 3, 4, 5]


def test_desert_fodder():
    instance = topo.Desert()
    assert instance.current_fodder() == 0


def test_Mountain_fodder():
    instance = topo.Mountain()
    assert instance.fodder == 0


def test_Ocean_fodder():
    instance = topo.Ocean()
    assert instance.fodder == 0
