# PyInductor

An unofficial Python port of Serge Stroobandt, ON4AA's ["Single-Layer Helical Round Wire Coil Inductor Calculator"](http://hamwaves.com/antennas/inductance.html)
(JavaScript [here](http://hamwaves.com/antennas/inductance/inductance.js)) with a few other additions (parameter tuning, temperature effects and sensitivity analysis).

This might be useful to some for designing air-core wire inductors (or helical antennas) for RF applications.

**1/2019 update**: Serge Stroobandt has ported his code from JavaScript to Brython (browser Python), so have a look.

## Requirements

* Python 2.7 (3.x should work with minimal changes)
* SciPy
* NumPy
* Matplotlib (only for plotting, can be removed with small changes)

## Differences

A notable difference is that this version requires the diameter of the coil former (`diam_former`) instead of the diameter of the former *plus* the wire. The additional temperature model is first order and only applies to the resistivity and physical dimensions of the wire, so be wary of this limitation.

Note that the results obtained with this version don't always match the original's (likely due to porting bugs) and that almost nothing has been properly validated, so proceed with caution. Also this port is possibly a bit outdated since the original may have been modified since its creation. 

## Usage

The most basic usage takes the physical dimensions, material properties and frequency of the inductor and returns a dictionary of calculated values (inductance, resonant frequency, etc.)

For example:

```python
from inductor import Inductor, MATERIALS

params = dict(N=6, diam_former=3e-3, diam_wire=1e-3, f=10e6, len_coil=8e-3)
params.update(MATERIALS['Cu, annealed'])

ind = Inductor(**params)
results = ind.analyze()

print results
```

gives:

```python
{'Rs_equiv': 0.0260142920022588, 'char_impedance': 1062.8882724816337, 'Ls_equiv': 4.18213766576639e-08, 'Rs_eff': 0.03933132499704669, 'Q_eff': 82.14705604747247, 'res_freq': 1088325440.0625987, 'Q_equiv': 101.01042124023245, 'skin_depth': 2.1102261245635593e-05, 'prop_factor': 0.5173362883660613, 'Ls_eff': 5.142220706528976e-08, 'Cp_equiv': 1.1309733366263994e-09}
```

For an explanation of these quantities see [here](http://hamwaves.com/antennas/inductance.html), and note in particular the difference between the effective series inducance (`Ls_eff`) and the frequency-independent equivalent inductance (`Ls_equiv`).

Tuning support is useful if you want to obtain (say) the necessary coil length for a desired inductance:

```python
from inductor import Inductor, MATERIALS

L_desired = 50e-9 # design a 50 nH inductor
params = dict(N=4, diam_former=5e-3, diam_wire=1.2e-3, f=100e6, len_coil=51e-3)
params.update(MATERIALS['Cu, annealed'])

ind = Inductor(**params)
print 'Initial length = %0.3f mm -> inductance = %0.3f nH' % (ind.len_coil/1e-3, ind.analyze()['Ls_eff']/1e-9)

ind.tune_parameter('len_coil', L_desired, input_range=(1e-3, 1))
print 'Tuned length = %0.3f mm -> inductance = %0.3f nH' % (ind.len_coil/1e-3, ind.analyze()['Ls_eff']/1e-9)
```

gives:

```
Initial length = 51.000 mm -> inductance = 94.515 nH
Tuned length = 10.838 mm -> inductance = 50.000 nH
```

You can also analyze the effect of changing an arbitrary input parameter (length, temperature, frequency, etc.) on an output quantity (inductance, Q, sensitivity, etc.). For example, you can obtain plots of the Q and self resonant frequency vs. wire diameter, while varying the length to fix the inductance:

![](http://i.imgur.com/RThvH.png)

You can also see how it affects the temperature coefficient of the inductance:

![](http://i.imgur.com/y5D2L.png)

See `test.py`, which has some random (and probably broken!) examples.


## Credit and license

All credit to Serge Stroobandt for his original version. License falls under his original GNU GPL version 3.

If you have any changes or fixes, then please free to send a pull request.
