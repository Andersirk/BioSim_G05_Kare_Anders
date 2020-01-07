# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

@pytest.fixture
def jungle_cell():
    """Return a simple island for used in various tests below"""
    return BioSim(island_map="OOOO\nOJSO\nOOOO", ini_pop=[], seed=1)
