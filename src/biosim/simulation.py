# -*- coding: utf-8 -*-

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"


import matplotlib.pyplot as plt
from biosim.island import Island
from biosim.animals import Herbivores, Carnivores
from biosim.cell_topography import Jungle, Savanna
import numpy as np
import random
import subprocess

_FFMPEG_BINARY = 'C:/Users/ander/OneDrive/Pictures/simtest/ffmpeeg/ffmpeg.exe'


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
        :param ymax_animals: Number specifying y-axis limit for graph showing
         animal numbers
        :param cmax_animals: Dict specifying color-code limits for
        animal densities
        :param img_base: String with beginning of file name for figures,
        including path
        :param img_fmt: String with file type for figures, e.g. 'png'

        If ymax_animals is None, the y-axis limit will be adjusted dynamically.

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
        self.add_population(ini_pop)
        self._current_year = 0
        self._final_year = None
        self.ymax_animals = ymax_animals
        self.cmax_animals = cmax_animals

        # attributes for saving images
        self._img_ctr = 0
        self._img_fmt = img_fmt
        self._img_base = img_base

        # Axes and figures to be instantiated in setup_sim_window
        self._sim_window_fig = None
        self._static_map_ax = None
        self._static_map_obj = None
        self._pop_plot_ax = None
        self._heat_herb_ax = None
        self._heat_herb_obj = None
        self._heat_carn_ax = None
        self._heat_carn_obj = None
        self._pop_pyram_ax = None
        self._pop_pyram_obj = None
        self._stack_area_ax = None
        self._stack_area_obj = None
        self._year_ax = None
        self._herb_cbar_ax = None
        self._carn_cbar_ax = None
        self.rgb_map = self._create_color_map(island_map)

        # Data variables for plots to be updated continuously
        self.y_stack = None
        self.herb_y = []
        self.carn_y = []

    def _setup_sim_window(self):
        """
        Instantiates the main figure widow and creates subplots for the
        different plots and heatmaps. Also does some setup regarding the
        subplot parameters.
        :return: None
        """
        plt.ion()
        # setup main window figure
        if self._sim_window_fig is None:
            self._sim_window_fig = plt.figure(figsize=(10, 5.63), dpi=150,
                                              facecolor="#ccd9ff")

        # setup static map axis and create the map object
        if self._static_map_ax is None:
            self._static_map_ax = self._sim_window_fig.add_subplot(2, 3, 1)
            self._static_map_obj = self._static_map_ax.imshow(self.rgb_map)

        # setup population subplot and some parameters for the subplot
        if self._pop_plot_ax is None:
            self._pop_plot_ax = self._sim_window_fig.add_subplot(2, 3, 4)
            self._pop_plot_ax.set_xlabel('Population', fontsize=9)
            if self.ymax_animals is not None:
                self._pop_plot_ax.set_ylim(0, self.ymax_animals)
        self._pop_plot_ax.set_xlim(0, self._final_year + 1)
        self._pop_plot_ax.tick_params(axis='both', which='major', labelsize=8)

        # setup herbivore heatmap subplot and accompanying colorbar axes
        if self._heat_herb_ax is None:
            self._heat_herb_ax = self._sim_window_fig.add_subplot(2, 3, 3)
            self._heat_herb_ax.tick_params(axis='both', which='major',
                                           labelsize=8)
            self._heat_herb_ax.set_xlabel('Herbivore heatmap', fontsize=9)
            self._herb_cbar_ax = self._sim_window_fig.add_axes(
                                                [0.715, 0.915, 0.25, 0.006])

        # setup carnivore heatmap subplot and accompanying colorbar axes
        if self._heat_carn_ax is None:
            self._heat_carn_ax = self._sim_window_fig.add_subplot(2, 3, 6)
            self._heat_carn_ax.tick_params(axis='both', which='major',
                                           labelsize=8)
            self._heat_carn_ax.set_xlabel('Carnivore heatmap', fontsize=9)
            self._carn_cbar_ax = self._sim_window_fig.add_axes(
                                                [0.715, 0.458, 0.25, 0.006])

        # setup population pyramid subplot and some parameters along with
        # text for labels
        if self._pop_pyram_ax is None:
            self._pop_pyram_ax = self._sim_window_fig.add_subplot(2, 3, 2)
            self._pop_pyram_obj = self._pop_pyram_ax.twiny()
            self._sim_window_fig.text(0.465, 0.495, 'Population size',
                                      fontsize=9)
            self._pop_pyram_obj.set_xlabel('Average weight', fontsize=9)
            self._sim_window_fig.text(0.648, 0.78, 'Age groups', fontsize=9,
                                      rotation=270)
            self._pop_pyram_ax.tick_params(axis='both', which='major',
                                           labelsize=8)
            self._pop_pyram_obj.tick_params(axis='both', which='major',
                                            labelsize=8)

        # setup stacked area subplot
        if self._stack_area_ax is None:
            self._stack_area_ax = self._sim_window_fig.add_subplot(2, 3, 5)
            self._stack_area_ax.tick_params(axis='both', which='major',
                                            labelsize=8)
            self._stack_area_ax.set_xlabel('Biomass', fontsize=9)
        self._instantiate_stacked_area()

        # setup year counter
        if self._year_ax is None:
            self._year_ax = self._sim_window_fig.text(
                0.04, 0.925, f'Year {self._current_year}', fontsize=18)

        self._sim_window_fig.tight_layout()

    def _save_graphics(self):
        """Saves graphics to file if file name is given."""
        if self._img_base is None:
            return
        self._sim_window_fig.savefig(
            f'{self._img_base}_{self._img_ctr:05d}.{self._img_fmt}',
            facecolor="#ccd9ff")
        self._img_ctr += 1

    def _update_population_plot(self):
        """
        Takes the total number of animal per species for the year it is called
        and appends them to the population plot y values, then plots the plot.
        if ymax is not set it adjusts the ymax the biggest value plotted + 500
        :return: None
        """
        carn_count, herb_count = self.island.total_number_per_species(
                                                                    ).values()
        self.carn_y.append(carn_count)
        self.herb_y.append(herb_count)
        self._pop_plot_ax.plot(range(0, self._current_year + 1),
                               self.herb_y, 'red', self.carn_y, 'lawngreen'
                               )
        if self.ymax_animals is None:
            self._pop_plot_ax.set_ylim(
                0, max(max(self.herb_y), max(self.carn_y)) + 500)

    def _instantiate_stacked_area(self):
        """
        Starts the stacked area plot "y" with nan values for the for length of
        num_years (in simulate(num_years)) when simulate is first called
        and appends to the existing "y" when called subsequently. When
        first instantiated it also sets some parameters for the plot,
        and adds a legend.
        :return: None
        """
        if self._stack_area_obj is None:
            nanstack = np.full(self._final_year, np.nan)
            self.y_stack = np.vstack([nanstack, nanstack, nanstack])
            self._stack_area_obj = self._stack_area_ax.stackplot(
                np.arange(0, self._final_year), self.y_stack,
                colors=['red', 'lawngreen', 'green'],
                labels=["Carnivores", "Herbivores", "Fodder"]
            )
            self._stack_area_ax.legend(fontsize='small', borderpad=0.1, loc=2)
        else:
            nanstack = np.full(self._final_year-self._current_year, np.nan)
            new_empty_values = np.vstack([nanstack, nanstack, nanstack])
            self.y_stack = np.append(self.y_stack, new_empty_values, axis=1)

    def _update_stacked_area(self):
        """
        Gets the current years biomass in a dictionary from
        "biomass_food_chain()" and updates the values form the stacked plot
        :return: None
        """
        biomassdict = self.island.biomass_food_chain()
        self.y_stack[0][self._current_year] = biomassdict["biomass_carnivores"]
        self.y_stack[1][self._current_year] = biomassdict["biomass_herbs"]
        self.y_stack[2][self._current_year] = biomassdict["biomass_fodder"]
        self._stack_area_ax.stackplot(np.arange(0, self._final_year),
                                      self.y_stack,
                                      colors=['red', 'lawngreen', 'green'])

    def _update_heatmap_herb(self, array):
        """
        Takes a numpy array with the same dimensions as the island and with
        the ammount of herbivores per cell, where row and col corresponds to
        the x and y of the island. The method sets up the heatmap and colorbar
        when simulate() is first called and updates the data for subsequent
        calls.
        :param array: A numpy array
        :return: None
        """
        if self._heat_herb_obj is None:
            self._heat_herb_obj = self._heat_herb_ax.imshow(
                array, interpolation='nearest', vmax=200, cmap='inferno'
            )
            herb_cbar = plt.colorbar(
                self._heat_herb_obj, cax=self._herb_cbar_ax,
                shrink=0.5, orientation='horizontal'
            )
            herb_cbar.ax.tick_params(labelsize=6)
            if self.cmax_animals is not None:
                self._heat_herb_obj.set_clim(
                    vmax=self.cmax_animals['Herbivore'])
        else:
            self._heat_herb_obj.set_data(array)

    def _update_heatmap_carn(self, array):
        """
        Takes a numpy array with the same dimensions as the island and with
        the ammount of carnivores per cell, where row and col corresponds to
        the x and y of the island. The method sets up the heatmap and colorbar
        when simulate() is first called and updates the data for subsequent
        calls.
        :param array: A numpy array
        :return: None
        """
        if self._heat_carn_obj is None:
            self._heat_carn_obj = self._heat_carn_ax.imshow(
                array, interpolation='nearest', vmax=200, cmap='inferno'
            )
            carn_cbar = plt.colorbar(
                self._heat_carn_obj, cax=self._carn_cbar_ax,
                shrink=0.5, orientation='horizontal'
            )
            carn_cbar.ax.tick_params(labelsize=6)
            if self.cmax_animals is not None:
                self._heat_carn_obj.set_clim(
                    vmax=self.cmax_animals['Carnivore'])
        else:
            self._heat_carn_obj.set_data(array)

    def _update_pop_pyram(self):
        """
        Creates/updates the population and biomass pyramid. This modifies
        the biomass bars from full bars to a line representing the bars extent
        it also automatically adjusts the xlimit of the populationnumbers
        while keeping 0 centered
        :return: None
        """
        herb_pop_per_age, carn_pop_per_age, herb_mean_w, carn_mean_w = \
            self.island.population_biomass_age_groups()
        age = ["0-1", "2-5", "5-10", "10-15", "15+"]
        [rectangle.remove() for rectangle in reversed(
                                                self._pop_pyram_obj.patches)]
        self._pop_pyram_ax.cla()
        self._pop_pyram_ax.barh(age, herb_pop_per_age, color='lawngreen')
        self._pop_pyram_ax.barh(age, carn_pop_per_age, color='red')
        rek1 = self._pop_pyram_obj.barh(age, herb_mean_w, color='black')
        rek2 = self._pop_pyram_obj.barh(age, carn_mean_w, color='black')
        maxlim = max(max(herb_pop_per_age), abs(min(carn_pop_per_age))) + 150
        self._pop_pyram_ax.set_xlim(-maxlim, maxlim)
        self._pop_pyram_obj.set_xticks(np.arange(-100, 101, step=20))
        for rectangle in rek1:
            rectangle.set_x(rectangle.get_width() - 1)
            rectangle.set_width(1)
        for rectangle in rek2:
            rectangle.set_x(rectangle.get_width() + 1)
            rectangle.set_width(1)

    def _update_sim_window(self):
        """
        This updates the main figure window the current years data.
        :return: None
        """
        herb_array, carn_array = self.island.arrays_for_heatmap()
        self._update_pop_pyram()
        self._update_heatmap_herb(herb_array)
        self._update_heatmap_carn(carn_array)
        self._update_population_plot()
        self._update_stacked_area()
        self._year_ax.set_text(f'Year {self._current_year}')
        plt.pause(1e-6)

    @staticmethod
    def _create_color_map(island_map_string):
        """
        Creates the basis for the static color map.
        :param island_map_string: Multi-line string specifying island geography
        :return: map_rgb : Nested list with a color value for each cell type
        """
        island_map_string = island_map_string.replace(" ", "")
        rgb_value = {'O': (0.0, 0.0, 1.0),  # blue
                     'M': (0.5, 0.5, 0.5),  # grey
                     'J': (0.0, 0.6, 0.0),  # dark green
                     'S': (0.5, 1.0, 0.5),  # light green
                     'D': (1.0, 1.0, 0.5)}  # light yellow

        map_rgb = [[rgb_value[column] for column in row]
                   for row in island_map_string.splitlines()]
        return map_rgb

    @staticmethod
    def set_animal_parameters(species, params):
        """
        Set parameters for animal species.

        :param species: String, name of animal species
        :param params: Dict with valid parameter specification for species
        """
        if species == "Herbivore":
            Herbivores.set_parameters(params)
        elif species == "Carnivore":
            Carnivores.set_parameters(params)
        else:
            raise ValueError(f"{species} is not a species in this simulation")

    @staticmethod
    def set_landscape_parameters(landscape, params):
        """
        Set parameters for landscape type.

        :param landscape: String, code letter for landscape
        :param params: Dict with valid parameter specification for landscape
        """
        if landscape == "J":
            Jungle.set_parameters(params)
        elif landscape == "S":
            Savanna.set_parameters(params)
        else:
            raise ValueError(
                f"{landscape} is not an acceptable"
                f" landscape code for setting parameters")

    def simulate(self, num_years, vis_years=1, img_years=None):
        """
        Run simulation while visualizing the result.

        :param num_years: number of years to simulate
        :param vis_years: years between visualization updates
        :param img_years: years between visualizations saved to files (
        default: vis_years)

        Image files will be numbered consecutively.
        """
        if img_years is None:
            img_years = vis_years
        self._final_year = self._current_year + num_years
        self._setup_sim_window()
        while self._current_year < self._final_year:
            self.island.annual_cycle()
            if self._current_year % vis_years == 0:
                self._update_sim_window()
            self._sim_window_fig.canvas.draw()
            if self._current_year % img_years == 0:
                self._save_graphics()
            self._current_year += 1

    def add_population(self, population):
        """
        Add a population to the island

        :param population: List of dictionaries specifying population
        """
        self.island.populate_island(population)

    @property
    def year(self):
        """Last year simulated."""
        return self._current_year

    @property
    def num_animals(self):
        """Total number of animals on island."""
        return sum(self.island.total_number_per_species().values())

    @property
    def num_animals_per_species(self):
        """Number of animals per species in island, as dictionary."""
        return self.island.total_number_per_species()

    @property
    def animal_distribution(self):
        """Pandas DataFrame with animal count per species
         for each cell on island."""
        return self.island.per_cell_count_pandas_dataframe()

    def make_movie(self):
        """Create MPEG4 movie from visualization images saved."""
        if self._img_base is None:
            raise RuntimeError("No filename defined.")
        try:
            # Parameters chosen according to
            # http://trac.ffmpeg.org/wiki/Encode/H.264,
            # section "Compatibility"
            subprocess.check_call([_FFMPEG_BINARY, '-framerate', '15',
                                   '-i', f'{self._img_base}_%05d.png',
                                   '-y',
                                   '-profile:v', 'baseline',
                                   '-level', '3.0',
                                   '-pix_fmt', 'yuv420p',
                                   f'{self._img_base}.mp4'])
        except subprocess.CalledProcessError as err:
            raise RuntimeError(f'ERROR: ffmpeg failed with: {err}')


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
                   {'species': 'Carnivore', 'age': 0, 'weight': 80} for _ in
                   range(100)]}
               ]
    simmert = BioSim(
        island_map, ini_pop, 1,
        img_base='C:/Users/ander/OneDrive/Pictures/simtest/testimg')
    # img_base = 'C:/Users/ander/OneDrive/Pictures/simtest/testimg'
    simmert.simulate(20)
    ini_pop2 = [{'loc': (1, 17), 'pop': [
        {'species': 'Carnivore', 'age': 0, 'weight': 80} for _ in
        range(100)]},
               {'loc': (1, 18), 'pop': [
                   {'species': 'Carnivore', 'age': 0, 'weight': 80} for _ in
                   range(99)]}
               ]
    simmert.add_population(ini_pop2)
    # simmert.simulate(20)
    # simmert.make_movie()
