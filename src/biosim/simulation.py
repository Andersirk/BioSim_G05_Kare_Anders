# -*- coding: utf-8 -*-

"""
"""

__author__ = "Kåre Johnsen & Anders Karlsen"
__email__ = "kajohnse@nmbu.no & anderska@nmbu.no"

import matplotlib.pyplot as plt
from biosim.Island import Island
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
        self.add_population(ini_pop)
        self._current_year = 0
        self.ymax_animals = ymax_animals
        plt.ion()

        self._img_ctr = 0
        self._img_fmt = img_fmt
        self._img_base = img_base

        self._final_year = None
        self._sim_window_fig = None
        self._static_map_sub = None
        self._static_map_ax = None
        self._pop_plot_sub = None
        self._heat_herb_sub = None
        self._heat_herb_im_ax = None
        self._heat_carn_sub = None
        self._heat_carn_im_ax = None
        self._pop_pyram_sub = None
        self._pop_pyram_ax = None
        self._stack_area_sub = None
        self._stack_area_ax = None
        self._year_ax = None

        self.rgbmap = self.create_color_map(island_map)
        self.y_stack = None
        self.herb_y = []
        self.carn_y = []

    def setup_sim_window(self):
        # setup main window
        if self._sim_window_fig is None:
            self._sim_window_fig = plt.figure(figsize=(10, 5.63), dpi=150, facecolor="#ccd9ff")

        # setup static
        if self._static_map_sub is None:
            self._static_map_sub = self._sim_window_fig.add_subplot(2, 3, 1)
            self._static_map_ax = self._static_map_sub.imshow(self.rgbmap)
        # setup populationplot
        if self._pop_plot_sub is None:
            self._pop_plot_sub = self._sim_window_fig.add_subplot(2, 3, 4)
            if self.ymax_animals is not None:
                self._pop_plot_sub.set_ylim(0, self.ymax_animals)
        self._pop_plot_sub.set_xlim(0, self._final_year + 1)
        self._pop_plot_sub.tick_params(axis='both', which='major', labelsize=8)

        # setup heatmaps
        if self._heat_herb_sub is None:
            self._heat_herb_sub = self._sim_window_fig.add_subplot(2, 3, 3)
            self._heat_herb_sub.tick_params(axis='both', which='major', labelsize=8)


        if self._heat_carn_sub is None:
            self._heat_carn_sub = self._sim_window_fig.add_subplot(2, 3, 6)
            self._heat_carn_sub.tick_params(axis='both', which='major',
                                            labelsize=8)

        #setup population pyramid
        if self._pop_pyram_sub is None:
            self._pop_pyram_sub = self._sim_window_fig.add_subplot(2, 3, 2)
            self._pop_pyram_ax = self._pop_pyram_sub.twiny()
            self._pop_pyram_sub.set_xlabel('Population size', fontsize=9)
            self._pop_pyram_ax.set_xlabel('Average weight', fontsize=9)
            self._pop_pyram_sub.tick_params(axis='both', which='major',
                         labelsize=8, labelrotation=30)
            self._pop_pyram_ax.tick_params(axis='both', which='major',
                         labelsize=8)
            #self._pop_pyram_sub.legend(fontsize= 'small', borderpad=0.1, loc=2)


        #setup stack area
        if self._stack_area_sub is None:
            self._stack_area_sub = self._sim_window_fig.add_subplot(2, 3, 5)
            self._stack_area_sub.tick_params(axis='both', which='major',
                                            labelsize=8)
        self._instantiate_stacked_area()

        if self._year_ax is None:
            self._year_ax = self._sim_window_fig.text(0.04, 0.925, f'Year {self._current_year}', fontsize=20)

        self._sim_window_fig.tight_layout()

    def _save_graphics(self):
        """Saves graphics to file if file name given."""
        if self._img_base is None:
            return
        self._sim_window_fig.savefig('{base}_{num:05d}.{type}'.format(base=self._img_base,
                                                     num=self._img_ctr,
                                                     type=self._img_fmt))
        self._img_ctr += 1


    def _update_population_plot(self):
        carn_count, herb_count = self.island.total_number_per_species().values()
        self.carn_y.append(carn_count)
        self.herb_y.append(herb_count)
        self._pop_plot_sub.plot(range(0,self._current_year+1), self.herb_y, 'red', self.carn_y, 'lawngreen')


    def _instantiate_stacked_area(self):
        if self._stack_area_ax is None:
            nanstack = np.full(self._final_year, np.nan)
            self.y_stack = np.vstack([nanstack, nanstack, nanstack])
            self._stack_area_ax = self._stack_area_sub.stackplot(np.arange(0, self._final_year), self.y_stack, colors=['red', 'lawngreen','green'], labels=["Carnivores", "Herbivores","Fodder"])
            self._stack_area_sub.legend(fontsize= 'small', borderpad=0.1, loc=2)
        else:
            nanstack= np.full(self._final_year-self._current_year, np.nan)
            new_empty_values = np.vstack([nanstack, nanstack, nanstack])
            self.y_stack = np.append(self.y_stack, new_empty_values, axis= 1)

    def _update_stacked_area(self, biomass_list):
        self.y_stack[0][self._current_year] = biomass_list["biomass_carnivores"]
        self.y_stack[1][self._current_year] = biomass_list["biomass_herbs"]
        self.y_stack[2][self._current_year] = biomass_list["biomass_fodder"]
        self._stack_area_sub.stackplot(np.arange(0, self._final_year), self.y_stack,
                                       colors=['red', 'lawngreen','green'])


    def _update_heatmap_herb(self, array):
        if self._heat_herb_im_ax is None:
            self._heat_herb_im_ax = self._heat_herb_sub.imshow(array, interpolation='nearest', vmax=400, cmap='inferno')
            self._heat_herb_im_ax.axes.get_xaxis().set_visible(False)
            self._heat_herb_im_ax.axes.get_yaxis().set_visible(False)
            self._sim_window_fig.colorbar(self._heat_herb_im_ax, ax=self._heat_herb_sub, shrink=0.5)
        else:
            self._heat_herb_im_ax.set_data(array)

    def _update_heatmap_carn(self, array):
        if self._heat_carn_im_ax is None:
            self._heat_carn_im_ax = self._heat_carn_sub.imshow(array, interpolation='nearest', vmax=100, cmap='inferno')
            self._sim_window_fig.colorbar(self._heat_carn_im_ax, ax=self._heat_carn_sub, shrink=0.5)
        else:
            self._heat_carn_im_ax.set_data(array)


    def update_pop_pyram(self):
        herb_list, carn_list, herb_mean_w_list, carn_mean_w_list = self.island.population_age_grups()
        age = ["0-1","2-5", "5-10", "10-15", "15+"]
        [p.remove() for p in reversed(self._pop_pyram_ax.patches)]
        self._pop_pyram_sub.cla()
        self._pop_pyram_sub.barh(age, herb_list, color='lawngreen')
        self._pop_pyram_sub.barh(age, carn_list, color='red')
        rek1 = self._pop_pyram_ax.barh(age, herb_mean_w_list, color='black')
        rek2 = self._pop_pyram_ax.barh(age, carn_mean_w_list, color='black')
        #maxticks= max(max(herb_list),abs(min(carn_list)))
        #self._pop_pyram_sub.set_xticks(np.arange(-maxticks, maxticks, step=(maxticks/100)))
        self._pop_pyram_sub.set_xticks(
            np.arange(-2000, 2001, step=500), )
        self._pop_pyram_ax.set_xticks(np.arange(-100, 101, step=20))
        for rektangle in rek1:
            rektangle.set_x(rektangle.get_width() - 1)
            rektangle.set_width(1)
        for rektangle in rek2:
            rektangle.set_x(rektangle.get_width() + 1)
            rektangle.set_width(1)

    def _update_sim_window(self):
        herb_array, carn_array = self.island.arrays_for_heatmap()
        self.update_pop_pyram()
        self._update_heatmap_herb(herb_array)
        self._update_heatmap_carn(carn_array)
        self._update_population_plot()
        if self.ymax_animals is None:
            self._pop_plot_sub.set_ylim(0, max(max(self.herb_y), max(self.carn_y)) + 500)
        self._update_stacked_area(self.island.biomass_food_chain())
        self._year_ax.set_text(f'Year {self._current_year}')
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
        if species == "Herbivore":
            Herbivores.set_parameters(params)
        elif species == "Carnivore":
            Carnivores.set_parameters(params)
        else:
            raise ValueError(f"{species} is not a species in this simulation")

    def set_landscape_parameters(self, landscape, params):
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
            raise ValueError(f"{landscape} is not an acceptable landscape code for setting parameters")


    def simulate(self, num_years, vis_years=1, img_years=None):
        """
        Run simulation while visualizing the result.

        :param num_years: number of years to simulate
        :param vis_years: years between visualization updates
        :param img_years: years between visualizations saved to files (default: vis_years)

        Image files will be numbered consecutively.
        """
        if img_years is None:
            img_years = vis_years
        self._final_year = self._current_year + num_years
        self.setup_sim_window()
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
        """Pandas DataFrame with animal count per species for each cell on island."""
        return self.island.per_cell_count_pandas_dataframe()

    def make_movie(self):
        """Create MPEG4 movie from visualization images saved."""
        if self._img_base is None:
                    raise RuntimeError("No filename defined.")
        try:
            # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
            # section "Compatibility"
            subprocess.check_call([_FFMPEG_BINARY, '-framerate', '15',
                                   '-i', '{}_%05d.png'.format(self._img_base),
                                   '-y',
                                   '-profile:v', 'baseline',
                                   '-level', '3.0',
                                   '-pix_fmt', 'yuv420p',
                                   '{}.{}'.format(self._img_base, "mp4")])
        except subprocess.CalledProcessError as err:
            raise RuntimeError('ERROR: ffmpeg failed with: {}'.format(err))



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
    simmert = BioSim(island_map, ini_pop, 1, img_base = 'C:/Users/ander/OneDrive/Pictures/simtest/testimg')
    #img_base = 'C:/Users/ander/OneDrive/Pictures/simtest/testimg'
    simmert.simulate(50)
    ini_pop2 = [{'loc': (1, 17), 'pop': [
        {'species': 'Carnivore', 'age': 0, 'weight': 80} for _ in
        range(100)]},
               {'loc': (1, 18), 'pop': [
                   {'species': 'Carnivore', 'age': 0, 'weight': 80} for _ in
                   range(100)]}
               ]
    simmert.add_population(ini_pop2)
    simmert.simulate(250)
    simmert.make_movie()

