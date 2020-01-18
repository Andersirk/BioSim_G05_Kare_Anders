# -*- coding: utf-8 -*-

"""
"""

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import matplotlib.pyplot as plt
from biosim.Island import Island
from biosim.animals import Animals
import numpy as np
import random


class BioSim:
    def __init__(
        self,
        island_map,
        ini_pop,
        seed,
        ymax_animals=None,
        cmax_animals=None,
        img_base=None,
        img_fmt="png",
    ):
        """
        :param island_map: Multi-line string specifying island geography
        :param ini_pop: List of dictionaries specifying initial population
        :param seed: Integer used as random number seed
        :param ymax_animals: Number specifying y-axis limit for graph showing animal numbers
        :param cmax_animals: Dict specifying color-code limits for animal densities
        :param img_base: String with beginning of file name for figures, including path
        :param img_fmt: String with file type for figures, e.g. 'png'

        If ymax_animals is None, the y-axis limit should be adjusted automatically.

        If cmax_animals is None, sensible, fixed default values should be used.
        cmax_animals is a dict mapping species names to numbers, e.g.,
           {'Herbivore': 50, 'Carnivore': 20}

        If img_base is None, no figures are written to file.
        Filenames are formed as

            '{}_{:05d}.{}'.format(img_base, img_no, img_fmt)

        where img_no are consecutive image numbers starting from 0.
        img_base should contain a path and beginning of a file name.
        """
        self.island = Island(island_map)
        random.seed(seed)
        self.island.populate_island(ini_pop)
        self.rgbmap = self.create_color_map(island_map)
        self._current_year = 0
        plt.ion()


        self._final_year = None
        self._sim_window_fig = None
        self._static_map_sub = None
        self._static_map_ax = None
        self._pop_plot_sub = None
        self._carn_line = None
        self._herb_line = None
        self._heat_herb_sub = None
        self._heat_herb_im_ax = None
        self._heat_carn_sub = None
        self._heat_carn_im_ax = None
        self._pop_pyram_sub = None
        self._pop_pyram_ax = None
        self._stack_area_sub = None
        self._stack_area_ax = None


    def setup_sim_window(self):
        # setup main window
        if self._sim_window_fig is None:
            self._sim_window_fig = plt.figure()

        # setup static
        if self._static_map_sub is None:
            self._static_map_sub = self._sim_window_fig.add_subplot(2, 3, 1)
            self._static_map_ax = self._static_map_sub.imshow(self.rgbmap)
        # setup populationplot
        if self._pop_plot_sub is None:
            self._pop_plot_sub = self._sim_window_fig.add_subplot(2, 3, 4)
            self._pop_plot_sub.set_ylim(0, 200)
        self._pop_plot_sub.set_xlim(0, self._final_year + 1)

        self._instantiate_herb_line()
        self._instantiate_carn_line()

        if self._heat_herb_sub is None:
            self._heat_herb_sub = self._sim_window_fig.add_subplot(2, 3, 3)

        if self._heat_herb_sub is None:
            self._heat_herb_sub = self._sim_window_fig.add_subplot(2, 3, 6)

        if self._pop_pyram_sub is None:
            self._pop_pyram_sub = self._sim_window_fig.add_subplot(2, 3, 2)

        if self._stack_area_sub is None:
            self._stack_area_sub = self._sim_window_fig.add_subplot(2, 3, 5)

        self._sim_window_fig.tight_layout()

    def _instantiate_herb_line(self):
        if self._herb_line is None:
            herb_plot = self._pop_plot_sub.plot(np.arange(0, self._final_year),
                                                np.full(self._final_year,
                                                        np.nan))
            self._herb_line = herb_plot[0]
        else:
            xdata, ydata = self._herb_line.get_data()
            xnew = np.arange(xdata[-1] + 1, self._final_year)
            if len(xnew) > 0:
                ynew = np.full(xnew.shape, np.nan)
                self._herb_line.set_data(np.hstack((xdata, xnew)),
                                         np.hstack((ydata, ynew)))

    def _instantiate_carn_line(self):
        if self._carn_line is None:
            carn_plot = self._pop_plot_sub.plot(np.arange(0, self._final_year),
                                           np.full(self._final_year, np.nan))
            self._carn_line = carn_plot[0]
        else:
            xdata, ydata = self._carn_line.get_data()
            xnew = np.arange(xdata[-1] + 1, self._final_year)
            if len(xnew) > 0:
                ynew = np.full(xnew.shape, np.nan)
                self._carn_line.set_data(np.hstack((xdata, xnew)),
                                         np.hstack((ydata, ynew)))

    def __instantiate_pop_pyram(self):
        pass

    def _update_herb_graph(self, herb_count):
        ydata = self._herb_line.get_ydata()
        ydata[self._current_year] = herb_count
        self._herb_line.set_ydata(ydata)

    def _update_carn_graph(self, carn_count):
        ydata = self._carn_line.get_ydata()
        ydata[self._current_year] = carn_count
        self._carn_line.set_ydata(ydata)

    def _update_sim_window(self):
        self._update_herb_graph(self.island.total_number_per_species()["Herbivore"])
        self._update_carn_graph(self.island.total_number_per_species()["Carnivore"])
        plt.pause(1e-6)

    def create_color_map(self, island_map):
        island_map = island_map.replace(" ", "")
        rgb_value = {'O': (0.0, 0.0, 1.0),  # blue
                     'M': (0.5, 0.5, 0.5),  # grey
                     'J': (0.0, 0.6, 0.0),  # dark green
                     'S': (0.5, 1.0, 0.5),  # light green
                     'D': (1.0, 1.0, 0.5)}  # light yellow

        kart_rgb = [[rgb_value[column] for column in row]
                    for row in island_map.splitlines()]
        return kart_rgb




    def set_animal_parameters(self, species, params):
        """
        Set parameters for animal species.

        :param species: String, name of animal species
        :param params: Dict with valid parameter specification for species
        """

    def set_landscape_parameters(self, landscape, params):
        """
        Set parameters for landscape type.

        :param landscape: String, code letter for landscape
        :param params: Dict with valid parameter specification for landscape
        """

    def simulate(self, num_years, vis_years=1, img_years=None):
        """
        Run simulation while visualizing the result.

        :param num_years: number of years to simulate
        :param vis_years: years between visualization updates
        :param img_years: years between visualizations saved to files (default: vis_years)

        Image files will be numbered consecutively.
        """
        if num_years is None:
            img_years = num_years
        self._final_year = self._current_year + num_years
        self.setup_sim_window()
        while self._current_year < self._final_year:
            self.island.annual_cycle()
            if self._current_year % vis_years == 0:
                self._update_sim_window()
            self._sim_window_fig.canvas.draw()
            self._current_year += 1



    def add_population(self, population):
        """
        Add a population to the island

        :param population: List of dictionaries specifying population
        """

    @property
    def year(self):
        """Last year simulated."""

    @property
    def num_animals(self):
        """Total number of animals on island."""

    @property
    def num_animals_per_species(self):
        """Number of animals per species in island, as dictionary."""
        return self.island.total_number_per_species()

    @property
    def animal_distribution(self):
        """Pandas DataFrame with animal count per species for each cell on island."""
        self.island.per_cell_count_pandas_dataframe()

    def make_movie(self):
        """Create MPEG4 movie from visualization images saved."""

if __name__ == "__main__":
    island_map = """\
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

    ini_pop = [{'loc': (1, 18), 'pop': [
        {'species': 'Herbivore', 'age': 0, 'weight': None} for _ in
        range(100)]},
               {'loc': (11, 8), 'pop': [
                   {'species': 'Carnivore', 'age': 0, 'weight': None} for _ in
                   range(100)]}
               ]
    simmert = BioSim(island_map, ini_pop, 1)
    simmert.simulate(50)

