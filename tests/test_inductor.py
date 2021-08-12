import sys
import pytest

from PyInductor import Inductor, MATERIALS


@pytest.mark.skipif(sys.version_info >= (3, 0), reason="requires python2.7")
def test_example_py2():
    params = dict(N=6, diam_former=3e-3, diam_wire=1e-3, f=10e6, len_coil=8e-3)
    params.update(MATERIALS['Cu, annealed'])

    ind = Inductor(**params)
    results = ind.analyze()

    assert results == {
        'Q_equiv': 101.01042124023245,
        'prop_factor': 0.5173362883660613,
        'Ls_equiv': 4.18213766576639e-08,
        'Q_eff': 82.14705604747247,
        'Rs_eff': 0.03933132499704669,
        'Rs_equiv': 0.0260142920022588,
        'Ls_eff': 5.142220706528976e-08,
        'skin_depth': 2.1102261245635593e-05,
        'char_impedance': 1062.8882724816337,
        'res_freq': 1088325440.0625987,
        'Cp_equiv': 1.1309733366263994e-09
    }


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
def test_example_py3():
    params = dict(N=6, diam_former=3e-3, diam_wire=1e-3, f=10e6, len_coil=8e-3)
    params.update(MATERIALS['Cu, annealed'])

    ind = Inductor(**params)
    results = ind.analyze()

    assert round(results['Q_equiv'], 6) == round(101.01042124023245, 6)
    assert results['prop_factor'] == 0.5173362883660613
    assert round(results['Ls_equiv'], 16) == round(4.18213766576639e-08, 16)
    assert round(results['Q_eff'], 7) == round(82.14705604747247, 7)
    assert round(results['Rs_eff'], 10) == round(0.03933132499704669, 10)
    assert round(results['Rs_equiv'], 10) == round(0.0260142920022588, 10)
    assert round(results['Ls_eff'], 16) == round(5.142220706528976e-08, 16)
    assert round(results['skin_depth'], 13) == round(2.1102261245635593e-05, 13)
    assert results['char_impedance'] == 1062.8882724816337
    assert results['res_freq'] == 1088325440.0625987
    assert round(results['Cp_equiv'], 16) == round(1.1309733366263994e-09, 16)
