from setuptools import setup

setup(name='PyInductor',
      version='0.0.0-dev',
      description='An unofficial Python port of Serge Stroobandt, ON4AA\'s "Single-Layer '
                  'Helical Round Wire Coil Inductor Calculator" (JavaScript here) with a '
                  'few other additions (parameter tuning, temperature effects and sensitivity '
                  'analysis).',
      url='https://github.com/roger-/PyInductor/',
      author='Roger D',
      license='GNU GPL v3',
      packages=['PyInductor'],
      zip_safe=False)
