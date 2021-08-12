import sys
import pytest

from math import pi
from PyInductor.phasing_coil_solver import Coil


@pytest.mark.skipif(sys.version_info >= (3, 0), reason="requires python2.7")
def test_phasing_coil_solver_py2(capsys):
    c = Coil(
        phase_shift_rad=pi,
        phase_shift_tolerance_pct=0.5,
        frequency=27e6,
        diam_wire_core=0.4e-3,
        diam_wire_with_isol_mm=2.7,
        N_range=(95, 100),
        diams_mm=[32],
        len_range_mm=(260, 310, 1),
    )
    c.solve()

    captured = capsys.readouterr()
    assert "N=95, diam_mm=32, len_mm=260.0, phi=3.12610513482" in captured.out
    assert "N=99, diam_mm=32, len_mm=309.0, phi=3.13512433923" in captured.out


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
def test_phasing_coil_solver_py3(capsys):
    c = Coil(
        phase_shift_rad=pi,
        phase_shift_tolerance_pct=0.5,
        frequency=27e6,
        diam_wire_core=0.4e-3,
        diam_wire_with_isol_mm=2.7,
        N_range=(95, 100),
        diams_mm=[32],
        len_range_mm=(260, 310, 1),
    )
    c.solve()

    captured = capsys.readouterr()
    assert "N=95, diam_mm=32, len_mm=260.0, phi=3.1261051348185567" in captured.out
    assert "N=99, diam_mm=32, len_mm=309.0, phi=3.1351243392302433" in captured.out
