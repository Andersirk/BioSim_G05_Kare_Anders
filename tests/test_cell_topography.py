# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import src.biosim.cell_topography as topo


def test_decrease_fodder_abundance():
    instance = topo.Topography()
    instance.fodder = 400
    decrease_amount = instance.decrease_fodder(200)
    assert decrease_amount == 200
    assert instance.current_fodder() == 200


def test_decrease_fodder_scarce():
    instance = topo.Topography()
    instance.fodder = 100
    decrease_amount = instance.decrease_fodder(200)
    assert decrease_amount == 100
    assert instance.current_fodder() == 0


def test_decrease_fodder_zero():
    instance = topo.Topography()
    instance.fodder = 0
    decrease_amount = instance.decrease_fodder(200)
    assert decrease_amount == 0
    assert instance.current_fodder() == 0
    

def test_current_occupants_int_test():
    instance = topo.Topography()
    assert type(instance.current_occupants()["Herbivores"]) == int and type(instance.current_occupants()["Carnivores"]) == int


def test_current_occupants_positive_test():
    instance = topo.Topography()
    assert instance.current_occupants()["Herbivores"] >= 0 and instance.current_occupants()["Carnivores"] >= 0


def test_animal_list_test():
    instance = topo.Topography()
    assert type(instance.animals) == list





