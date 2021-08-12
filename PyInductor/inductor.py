from __future__ import division

import numpy as np
from PyInductor.data import MATERIALS, proximity_factor
from scipy.special import kn, iv
from scipy.constants import mu_0, c
# from pylab import *
from scipy.optimize import newton, minimize_scalar
# from scipy.optimize import fminbound
from scipy.misc import derivative
from math import pi, sqrt


class Inductor(object):
    mu_r_core = 1
    temperature = 25

    def __init__(self, **kwargs):
        self.set_params(**kwargs)

        self.reference_temperature = self.temperature

    def set_params(self, **kwargs):
        for param, value in kwargs.items():
            setattr(self, param, value)

    def tune_parameter(self, input_param_name, output_target_val, input_range=(0, np.inf),
                       output_param_name='Ls_eff', percent_tol=1):
        # TODO: extra parameter to optimize
        '''
        Vary parameter 'input_param_name' so that output 'output_param_name' achieves
        a value of 'output_target_val'.
        '''
        def objective(value):
            setattr(self, input_param_name, value)
            val = (1e9 * self.analyze()[output_param_name] - 1e9 * output_target_val) ** 2

            return val

        # new_param_value = fminbound(objective, *param_range, full_output=False)
        new_param_value = minimize_scalar(objective, bounds=input_range, method='bounded').x

        setattr(self, input_param_name, new_param_value)

        error = 100 * (self.analyze()[output_param_name] - output_target_val) / output_target_val
        if abs(error) > percent_tol:
            raise Exception('achieved error of %0.2f %% does not meet requirement' % error)

        return new_param_value

    def temperature_expan_factor(self):
        dT = (self.temperature - self.reference_temperature)
        return (1 + self.temp_coeff_expan * dT)

    @property
    def diam_former(self):
        dT = (self.temperature - self.reference_temperature)
        diam_coil = self._diam_former + self._diam_wire
        wire_len_squared = self.len_coil**2 + (np.pi * self.N * diam_coil) ** 2
        scale_factor = 1 + dT * self.temp_coeff_expan * wire_len_squared / (
            wire_len_squared - self.len_coil ** 2)

        # new_diam = self._diam_former + (
        #     self.len_coil / np.pi / self.N) ** 2 * self.temp_coeff_expan * dT / (
        #     self._diam_former + self._diam_wire)
        new_diam = diam_coil * scale_factor - self.diam_wire
        # new_diam2 = self._diam_former * self.temperature_expan_factor()

        # print('old diam {}'.format(self._diam_former))
        # print('new diam {}'.format(new_diam))
        # print('new diam2 {}'.format(new_diam2))

        return new_diam

    @diam_former.setter
    def diam_former(self, value):
        self._diam_former = value

    @property
    def diam_wire(self):
        return self._diam_wire * self.temperature_expan_factor()

    @diam_wire.setter
    def diam_wire(self, value):
        self._diam_wire = value

    @property
    def rho(self):
        temp_factor = (1 + self.temp_coeff_rho * (self.temperature - self.rho_t0))
        return self._rho * temp_factor

    @rho.setter
    def rho(self, value):
        self._rho = value

    def sensitivity(self, input_name, output_name='Ls_eff', delta=0.01, normalize=True):
        old_p = getattr(self, input_name)
        d_in = delta * old_p

        def _func(value):
            setattr(self, input_name, value)

            return self.analyze()[output_name]

        d_out_d_in = derivative(_func, old_p, dx=d_in, order=3)
        setattr(self, input_name, old_p)

        if normalize:
            s = (d_out_d_in) * old_p / (self.analyze()[output_name])
        else:
            s = d_out_d_in / (self.analyze()[output_name])

        return s

    @property
    def turn_spacing(self):
        return self.len_coil / self.N - self.diam_wire

    def analyze(self, **new_params):
        if new_params:
            self.set_params(**new_params)

        diam_coil = self.diam_former + self.diam_wire

        '''if self.N*self.diam_wire > self.len_coil:
            raise Exception('physically unrealizable values (reduce self.N*self.diam_wire)')

        if self.diam_wire > diam_coil:
            raise Exception('physically unrealizable values (reduce self.diam_wire)')'''

        pitch = self.len_coil / self.N
        phi = proximity_factor(self.len_coil / diam_coil, self.diam_wire / pitch)
        omega = 2 * np.pi * self.f

        # effective diameter of coil
        D_eff = diam_coil - self.diam_wire * (1 - 1 / np.sqrt(phi))

        # effective pitch angle
        psi = np.arctan(pitch / (np.pi * D_eff))

        # field non-uniformity correction factor according to Lundin
        if D_eff >= self.len_coil:
            k_L = (1 + 0.383901 * np.power(self.len_coil / D_eff, 2) + 0.017108 * np.power(
                self.len_coil / D_eff, 4)) / (1 + 0.258952 * np.power(self.len_coil / D_eff, 2))

            k_L = k_L * (np.log(4 * D_eff / self.len_coil) - 0.5)
            k_L += 0.093842 * np.power(self.len_coil / D_eff, 2) + 0.002029 * np.power(
                self.len_coil / D_eff, 4) - 0.000801 * np.power(self.len_coil / D_eff, 6)
            k_L *= (2 / np.pi) * (self.len_coil / D_eff)
        else:
            k_L = (1 + 0.383901 * np.power(D_eff / self.len_coil, 2) + 0.017108 * np.power(
                D_eff / self.len_coil, 4)) / (1 + 0.258952 * np.power(D_eff / self.len_coil, 2))
            k_L -= (4 / 3 / np.pi) * (D_eff / self.len_coil)

        # round wire self-inductance correction factor according to Rosa
        k_s = 5 / 4 - np.log(2 * pitch / self.diam_wire)

        # round wire mutual-inductance correction factor according to Grover and Knight
        k_m = -0.16725 / self.N + 0.0033 / self.N**2
        k_m *= np.log(self.N)
        k_m += 0.337883 * (1 - 0.9754 / (self.N - 0.0246))

        # effective length of wire
        len_wire_eff = np.hypot(self.N * np.pi * D_eff, self.len_coil)

        # skin depth
        sigma = 1 / self.rho
        delta_i = 1 / np.sqrt(np.pi * self.f * mu_0 * self.mu_r * sigma)

        # effective series AC resistance
        Rs_eff = self.rho * len_wire_eff / (np.pi * (self.diam_wire * delta_i - delta_i ** 2)) * phi
        if self.N > 1:
            Rs_eff *= (self.N - 1) / self.N

        # frequency-independent series inductance
        Ls = self.mu_r_core * mu_0 * np.pi * (D_eff * self.N) ** 2 / 4 / self.len_coil * k_L
        Ls -= self.mu_r_core * mu_0 * D_eff * self.N * (k_s + k_m) / 2

        # numerically find radial wave number
        k0 = omega / c
        a = D_eff / 2

        h1 = k0 / np.tan(psi) ** 2  # beta estimate
        h2 = k0

        def _func(h):
            return helix_dispersion(h, a, psi, k0)
        h = newton(_func, (h1 + h2) / 2)

        # characteristic impedance
        beta = h2beta(h, k0)
        Z_0 = 60 / k0 * beta * iv(0, h * a) * kn(0, h * a)

        # effective series inductance at design frequency
        Leffs = Z_0 / omega * np.tan(beta * self.len_coil) * k_L
        Leffs -= self.mu_r_core * mu_0 * D_eff * self.N * (k_s + k_m) / 2

        # effective unloaded quality factor
        Xeffs = omega * Leffs
        Qeff = Xeffs / Rs_eff

        # unloaded quality factor
        Reffp = (Qeff**2 + 1) * Rs_eff
        XLs = omega * Ls
        RLs = (Reffp - np.sqrt(np.power(Reffp, 2) - 4 * np.power(XLs, 2))) / 2
        QL = XLs / RLs

        # parallel stray capacitance
        XLp = (np.power(QL, 2) + 1) / np.power(QL, 2) * XLs
        Xeffp = (np.power(Qeff, 2) + 1) / np.power(Qeff, 2) * Xeffs
        XCLp = Xeffp * XLp / (XLp - Xeffp)
        CLp = -1 / omega / XCLp

        # find parallel resonant frequency
        # FIXME: Doesn't agree w/ Javascript version!

        def _func2(w):
            B_res = (pi / 2) / self.len_coil
            k0 = w / c
            h = sqrt(B_res**2 - k0**2)

            return helix_dispersion(h, a, psi, k0)**2

        # w_res = fminbound(_func2, c / len_wire_eff / 40, 1 * c / len_wire_eff * pi / 2)
        w_res = minimize_scalar(_func2, bounds=(
            c / len_wire_eff / 40, 1 * c / len_wire_eff * pi / 2), method='bounded').x

        # save all results
        results = {}
        results['char_impedance'] = float(Z_0)
        results['skin_depth'] = float(delta_i)
        results['prop_factor'] = float(beta)
        results['Ls_eff'] = float(Leffs)
        results['Rs_eff'] = float(Rs_eff)
        results['Q_eff'] = float(Qeff)
        results['Ls_equiv'] = float(Ls)
        results['Rs_equiv'] = float(RLs)
        results['Cp_equiv'] = float(CLp)
        results['Q_equiv'] = float(QL)
        results['res_freq'] = float(w_res / 2 / pi)

        return results


def helix_dispersion(h, a, psi, k0):
    fh = kn(1, h * a) * iv(1, h * a) / kn(0, h * a) / iv(0, h * a) - (h / k0 * np.tan(psi)) ** 2

    return fh


def h2beta(h, k0):
    return np.hypot(k0, h)


def main():
    params = dict(N=6, diam_former=3e-3, diam_wire=1e-3, f=10e6, len_coil=8e-3)
    params.update(MATERIALS['Cu, annealed'])

    ind = Inductor(**params)
    results = ind.analyze()

    print(results)


if __name__ == '__main__':
    main()
