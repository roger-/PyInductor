from __future__ import division

import warnings

from datetime import datetime
from multiprocessing import Pool, cpu_count
from itertools import product
from PyInductor.inductor import Inductor, MATERIALS

warnings.filterwarnings("ignore")


def _solver(combination):
    """This is the core of the solver, which takes one combination of coil parameters and
    analyzes the inductor. If the resulting phi is within the allowed tolerance, the coil
    parameters are returned."""

    # extract the changing params
    n, diam_mm, len_um, coil_params = combination
    # extract the static params
    params = {'N': n,
              'diam_former': (diam_mm + coil_params['diam_wire_with_isol_mm']) * 1e-3,
              'diam_wire': coil_params['diam_wire_core_mm'] * 1e-3,
              'f': coil_params['frequency'],
              'len_coil': len_um * 1e-6}
    params.update(coil_params['material'])
    try:
        ind = Inductor(**params)
        results = ind.analyze()
    except RuntimeError:
        return None

    phi = results['prop_factor'] * len_um * 1e-6
    # if phi is within the allowed tolerance
    if (coil_params['phase_shift_rad'] * (
            1 - coil_params['phase_shift_tolerance_pct'] / 100)) < phi < (
            coil_params['phase_shift_rad'] * (1 + coil_params['phase_shift_tolerance_pct'] / 100)):

        # we only want 1 wire layer for the winding, don't we?
        if ind.turn_spacing <= 0:
            return None

        # return coil parameters: N of threads, diameter, length and the resulting phi
        return "N={n}, diam_mm={diam_mm}, len_mm={len_mm}, phi={phi}".format(
            n=n, diam_mm=diam_mm, len_mm=len_um * 1e-3, phi=phi)


class PhasingCoilSolver:
    def __init__(self, phase_shift_rad, phase_shift_tolerance_pct, frequency, diam_wire_core_mm,
                 diam_wire_with_isol_mm, N_range, diams_mm, len_range_mm, material, ncpus=0):
        """
        Parameters:
        phase_shift_rad (float): Phase shift we want to achieve
        phase_shift_tolerance_pct (float): Relative allowed phase shift difference (+/- percent)
        frequency (float): center frequency
        diam_wire_core_mm (float): Diameter of the wire's core
        diam_wire_with_isol_mm (float): Diameter of the wire including insulation
        N_range (tuple): Range of coil threads for which to perform the calculations,
                         e.g. (10, 100)
        diams_mm (list): List of coil diameters, e.g. [16, 20, 25, 32, 100, 125, 1500]
                         This makes better sense than defining a range, because available
                         tubes/pipes have fixed diameter and we usually want to choose one of
                         them, rather than manufacture a pipe/tube with a specific diameter.
        len_range_mm (tuple): Range of coil lenghts for which to perform the calculations,
                              incl. step, e.g. (20, 300, 1)
        material (str): String defining the material of wire. See PyInductor.data for what's
                        supported.
        ncpus (int): Number of CPUs we want to utilize; if set to zero, it defaults to
                     number of available CPUs minus one which is reasonable for most cases.
        """

        self.phase_shift_rad = phase_shift_rad
        self.phase_shift_tolerance_pct = phase_shift_tolerance_pct
        self.frequency = frequency
        self.diam_wire_core_mm = diam_wire_core_mm
        self.diam_wire_with_isol_mm = diam_wire_with_isol_mm
        self.N_range = N_range
        self.diams_mm = diams_mm
        self.len_range_mm = len_range_mm
        self.material = MATERIALS[material]
        if ncpus:
            self.ncpus = ncpus
        else:
            self.ncpus = (cpu_count() - 1) if cpu_count() >= 2 else 1

    def solve(self):

        pool = Pool(processes=self.ncpus)

        len_range_um = [int(l_mm * 1e3) for l_mm in self.len_range_mm]
        # generate all possible combinations
        combinations = product(range(self.N_range[0],  # start value
                                     self.N_range[1] + 1),  # end value
                               self.diams_mm,
                               range(len_range_um[0],  # start value
                                     len_range_um[1] + len_range_um[2],  # incl. end value
                                     len_range_um[2]))  # step
        # attach coil static parameters to the combinations
        combinations_with_static_params = [c + (self.__dict__,) for c in combinations]

        print("{begin_end} Processing started with {ncpus} procs {begin_end}".format(
            begin_end=10 * "-", ncpus=self.ncpus))
        dt_start = datetime.now()

        # feed the process pool with the data (generated combinations + static coil params)
        for out in pool.imap_unordered(_solver, combinations_with_static_params):
            if out:
                print(out)

        print("{begin_end} Processing stopped. Time consumed: {timedelta} {begin_end}".format(
            begin_end=10 * "-", timedelta=datetime.now() - dt_start))
