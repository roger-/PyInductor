import sys
import pytest

from math import pi
from PyInductor.phasing_coil_solver import PhasingCoilSolver

test_solver1 = dict(phase_shift_rad=pi,
                    phase_shift_tolerance_pct=0.5,
                    frequency=27e6,
                    diam_wire_core_mm=0.4,
                    diam_wire_with_isol_mm=2.7,
                    N_range=(95, 99),
                    diams_mm=[32],
                    len_range_mm=(260, 310, 1),
                    material='Cu, annealed')


@pytest.mark.skipif(sys.version_info >= (3, 0), reason="requires python2.7")
class TestPy2:
    def test_phasing_coil_solver(self, capsys):
        s = PhasingCoilSolver(**test_solver1)
        s.solve()

        captured = capsys.readouterr()
        assert ("N=95, diameter_mm=32, length_mm=260.0, phi=3.12610513482, "
                "turn_spacing_mm=0.0368421052632") in captured.out
        assert ("N=99, diameter_mm=32, length_mm=310.0, phi=3.13226639014, "
                "turn_spacing_mm=0.431313131313") in captured.out

    # STOP adding new Python 2 tests!!!
    # STOP adding new Python 2 tests!!!
    # STOP adding new Python 2 tests!!!


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
class TestPy3:
    def test_phasing_coil_solver(self, capsys):
        s = PhasingCoilSolver(**test_solver1)
        s.solve()

        captured = capsys.readouterr()
        assert ("N=95, diameter_mm=32, length_mm=260.0, phi=3.1261051348185567, "
                "turn_spacing_mm=0.03684210526315789") in captured.out
        assert ("N=99, diameter_mm=32, length_mm=310.0, phi=3.1322663901436427, "
                "turn_spacing_mm=0.4313131313131312") in captured.out

    def test_phasing_coil_solver_with_max_turn_spacing_limit(self, capsys):
        test_solver2 = test_solver1.copy()
        test_solver2['max_turn_spacing_mm'] = 0.2

        s = PhasingCoilSolver(**test_solver2)
        s.solve()

        captured = capsys.readouterr()
        assert ("N=95, diameter_mm=32, length_mm=260.0, phi=3.1261051348185567, "
                "turn_spacing_mm=0.03684210526315789") in captured.out
        assert ("N=99, diameter_mm=32, length_mm=310.0, phi=3.1322663901436427, "
                "turn_spacing_mm=0.4313131313131312") not in captured.out
