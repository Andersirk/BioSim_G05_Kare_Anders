# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import src.biosim.cell_topography as topo
import pytest

@pytest.fixture
def basic_topography():
    return topo.Topography()

@pytest.mark.parametrize("fodder, requested, dec_amunt, fodder_result",
                         [(400, 200, 200, 200),
                          (100, 200, 100, 0),
                          (0, 200, 0, 0 )])

def test_Topo_decrease_fodder_abundance(basic_topography, fodder, requested, dec_amunt, fodder_result):
    """Tests that the amount of fodder can be decreased"""
    basic_topography.fodder = fodder
    decrease_amount = basic_topography.decrease_fodder(requested)
    assert decrease_amount == dec_amunt
    assert basic_topography.current_fodder() == fodder_result


# def test_Topo_decrease_fodder_scarce(basic_topography):
#     """Tests that the fodder decrease stops when the amount is zero """
#     basic_topography.fodder = 100
#     decrease_amount = basic_topography.decrease_fodder(200)
#     assert decrease_amount == 100
#     assert basic_topography.current_fodder() == 0
#
#
# def test_Topo_decrease_fodder_zero(basic_topography):
#     """Tests that the amount of fodder cant be decrased if the current amount of food allredy is zero"""
#     basic_topography.fodder = 0
#     decrease_amount = basic_topography.decrease_fodder(200)
#     assert decrease_amount == 0
#     assert basic_topography.current_fodder() == 0
#

def test_Topo_current_occupants_int():
    """Test that the numbers of herbivore and carnivores occupants in a cell is an int"""
    instance = topo.Topography()
    assert type(instance.current_occupants()["Herbivores"]) == int and type(instance.current_occupants()["Carnivores"]) == int


def test_Topo_current_occupants_positive():
    """Test that the numbers of herbivore and carnivores occupants in a cell is either 0 or positive"""
    instance = topo.Topography()
    assert instance.current_occupants()["Herbivores"] >= 0 and instance.current_occupants()["Carnivores"] >= 0


def test_Topo_current_fodder():
    """Test that the amount of fodder is a float and greater than 0"""
    instance = topo.Topography()
    assert type(instance.current_fodder()) == float and instance.current_fodder() >= 0


def test_Topo_remove_animal():
    """Tests that an emigranting animal can be removed from its old cells animal list"""
    instance = topo.Topography()
    instance.animals = [1, 2, 3, 4]
    instance.remove_animal(4)
    assert instance.animals == [1, 2, 3]


def test_Topo_add_animal():
    """Tests that an imigranting animal can be added to the new cells animal list"""
    instance = topo.Topography()
    instance.animals = [1, 2, 3, 4]
    instance.add_animal(5)
    assert instance.animals == [1, 2, 3, 4, 5]


def test_desert_fodder():
    """Tests that the desert dont have any fooder"""
    instance = topo.Desert()
    assert instance.current_fodder() == 0


def test_Mountain_fodder():
    """Tests that the mountains dont have any fooder"""
    instance = topo.Mountain()
    assert instance.fodder == 0


def test_Ocean_fodder():
    """Tests that the oceans dont have any fooder"""
    instance = topo.Ocean()
    assert instance.fodder == 0
