from __future__ import division

import warnings

from datetime import datetime
from multiprocessing import Pool, cpu_count
from itertools import product
from PyInductor.inductor import Inductor, MATERIALS

warnings.filterwarnings("ignore")


def _solver(combination):
    n, diam_mm, len_um, coil_parms = combination
    params = {'N': n,
              'diam_former': (diam_mm + coil_parms['diam_wire_with_isol_mm']) * 1e-3,
              'diam_wire': coil_parms['diam_wire_core'],
              'f': coil_parms['frequency'],
              'len_coil': len_um * 1e-6}
    params.update(MATERIALS['Cu, annealed'])
    try:
        ind = Inductor(**params)
        results = ind.analyze()
    except RuntimeError:
        return None

    x = results['prop_factor'] * len_um * 1e-6
    if (coil_parms['phase_shift_rad'] * (1 - coil_parms['phase_shift_tolerance_pct'] / 100)) < x < (
            coil_parms['phase_shift_rad'] * (1 + coil_parms['phase_shift_tolerance_pct'] / 100)):

        # we only want 1 wire layer for the winding, don't we?
        len_mm = len_um * 1e-3
        if len_mm < coil_parms['diam_wire_with_isol_mm'] * n:
            return None

        return "N={n}, diam_mm={diam_mm}, len_mm={len_mm}, phi={x}".format(
            n=n, diam_mm=diam_mm, len_mm=len_mm, x=x)


class Coil:
    def __init__(self, phase_shift_rad, phase_shift_tolerance_pct, frequency, diam_wire_core,
                 diam_wire_with_isol_mm, N_range, diams_mm, len_range_mm, ncpus=0):
        self.phase_shift_rad = phase_shift_rad
        self.phase_shift_tolerance_pct = phase_shift_tolerance_pct
        self.frequency = frequency
        self.diam_wire_core = diam_wire_core
        self.diam_wire_with_isol_mm = diam_wire_with_isol_mm
        self.N_range = N_range
        self.diams_mm = diams_mm
        self.len_range_mm = len_range_mm
        if ncpus:
            self.ncpus = ncpus
        else:
            self.ncpus = (cpu_count() - 1) if cpu_count() >= 2 else 1

    def solve(self):

        ncpus = (cpu_count() - 1) if cpu_count() >= 2 else 1
        pool = Pool(processes=ncpus)

        len_range_um = (int(l_mm * 1e3) for l_mm in self.len_range_mm)
        combinations = product(range(*self.N_range), self.diams_mm, range(*len_range_um))
        combinations = [c + (self.__dict__,) for c in combinations]

        print("{begin_end} Processing started with {ncpus} procs {begin_end}".format(
            begin_end=10 * "-", ncpus=ncpus))
        dt_start = datetime.now()

        for out in pool.imap_unordered(_solver, combinations):
            if out:
                print(out)

        print("{begin_end} Processing stopped. Time consumed: {timedelta} {begin_end}".format(
            begin_end=10 * "-", timedelta=datetime.now() - dt_start))
