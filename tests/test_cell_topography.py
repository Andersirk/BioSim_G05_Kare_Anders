# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import src.biosim.cell_topography as topo


def test_test():
    ke=topo.Jungle()
    assert ke.fodder == 800

#
# def test_current_occupants_int_test():
#     instance = topo.Topography()
#     assert type(instance.herbivore_count) == int and type(instance.carnivore_count) == int
#
#
# def test_current_occupants_positive_test():
#     instance = topo.Topography()
#     assert type(instance.herbivore_count) >= 0 and type(instance.carnivore_count) >= 0
#

def test_animal_list_test():
    instance = topo.Topography()
    assert type(instance.animals) == list





