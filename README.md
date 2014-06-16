# PyInductance

An unofficial Python port of Serge Stroobandt, ON4AA's ["Single-Layer Helical Round Wire Coil Inductor Calculator"](http://hamwaves.com/antennas/inductance.html)
(JavaScript [here](http://hamwaves.com/antennas/inductance/inductance.js)) with a few other additions (parameter tuning, temperature effects and sensitivity analysis).

This might be useful to some for designing air-core wire inductors for RF applications.

# Note

Note that the results obtained with this version don't always match the original (likely due to bugs in this one), and that this one is likely a bit outdated. Also almost none of the results obtained have been validated, so proceed with caution. 

Finally note this version requires the diameter of the coil former (`diam_former`) instead of the diameter of the former *plus* the wire.

# Usage

The most basic usage takes the physical dimentions, material properties and frequency of the inductor and will return a dictionary of calculated values (inductance,
resonant frequency, etc.)

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

Tuning support is useful if you want to obtain (say) the necessary length for a given inductance:

```python
from inductor import Inductor, MATERIALS

L_desired = 50e-9
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

You can also analyze the effect of changing an arbitrary input parameter (length, frequency, etc.) on an output quantity (inductance, Q, temperature sensitivity, etc.)

For example you can obtain plots like this (see `test.py`):

![](http://i.imgur.com/RThvH.png)

![](http://i.imgur.com/y5D2L.png)

# Credit

All credit to Serge Stroobandt for his original version. License falls under his original GNU GPL version 3.

If you have any changes or fixed, then please free to send a pull request.
