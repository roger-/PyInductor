from __future__ import division
from pylab import *
from inductor import *


def main():
    params = dict(N=6, diam_former=3e-3, diam_wire=1.2e-3, f=100e6, len_coil=5e-3)
    params.update(MATERIALS['Cu, annealed'])

    ind = Inductor(**params)
    #print ind.analyze()

    L_target = 200e-9
    diam_wires = linspace(5, 10)
    fres = []
    qs = []
    lens = []
    temp_sensi = []

    for d in diam_wires:
        print d
        ind.N = d

        ind.tune_parameter('len_coil', L_target, param_range=(ind.N*ind.diam_wire, 1))

        result = ind.analyze()
        fres.append(result['res_freq'])
        qs.append(result['Q_eff'])
        lens.append(ind.len_coil)

        s = ind.sensitivity('temperature', normalize=False)
        temp_sensi.append(s)

    figure()
    plot(diam_wires/1e-3, array(fres)/1e6, color='red')
    ylabel('Self-resonant frequency (MHz)', color='red')
    xlabel('Wire diameter (mm)')

    title('L = 80 nH (fixed, coil length varies), Q @ 100 MHz')

    twinx()
    #figure()
    plot(diam_wires/1e-3, qs, color='blue')
    ylabel('Q factor', color='blue')

    figure()
    plot(diam_wires/1e-3, array(temp_sensi)*1e6)
    ylabel('Temperature coefficient (ppm/$\degree$C)')
    xlabel('Wire diameter (mm)')

    show()

def main3():
    params = dict(N=6, diam_former=3e-3, diam_wire=1e-3, f=10e6, len_coil=8e-3)
    params.update(MATERIALS['Cu, annealed'])

    ind = Inductor(**params)
    print ind.analyze()

    print 'current Ls', ind.analyze()['Ls_eff']
    print 'current Q', ind.analyze()['Q_eff']

    #return

    #print 'param tunes to', ind.tune_parameter('len_coil', 50e-9, param_range=(0, 50e-3))

    print 'Q_eff sensi', 100*ind.sensitivity('N', 'Q_eff')
    print 'Ls_eff sensi', 100*ind.sensitivity('N', 'Ls_eff')

    input_values = linspace(1, 1000, 50)*1e6
    qs = zeros(len(input_values))
    sensi = zeros(len(input_values))
    coil_len = zeros(len(input_values))
    Ls = zeros(len(input_values))

    for i, inp in enumerate(input_values):
        ind.f = inp
        '''try:
            ind.tune_parameter('len_coil', 100e-9, param_range=(ind.N*ind.diam_wire, 100e-3))
        except:
            continue'''

        results = ind.analyze()
        qs[i] = results['Q_eff']
        Ls[i] = results['Ls_eff']

        sensi[i] = ind.sensitivity('temperature', 'Ls_eff', normalize=False)
        coil_len[i] = ind.turn_spacing

    figure()
    plot(input_values, qs)
    title('Q')

    figure()
    plot(input_values, 1e6*sensi)
    title('Sensitivity')

    figure()
    plot(input_values, coil_len)
    title('coil spacing')

    figure()
    plot(input_values, Ls/1e-9)
    title('induct')

    show()




def main2():
    params = dict(N=4, diam_former=5e-3, diam_wire=1.2e-3, f=100e6, len_coil=51e-3)
    params.update(MATERIALS['Cu, annealed'])

    L_desired = 50e-9

    ind = Inductor(**params)

    print 'Initial length = %0.3f mm -> inductance = %0.3f nH' % (ind.len_coil/1e-3, ind.analyze()['Ls_eff']/1e-9)

    #ind.tune_parameter('len_coil', L_desired, input_range=(ind.N*ind.diam_wire, 1))
    ind.tune_parameter('len_coil', L_desired, input_range=(1e-3, 1))

    print ind.N*ind.diam_wire


    print '> Tuned length = %0.3f mm -> inductance = %0.3f nH' % (ind.len_coil/1e-3, ind.analyze()['Ls_eff']/1e-9)

    print ind.analyze()

    lens = linspace(ind.N*ind.diam_wire, 100e-3, 100)

    inds = [ind.analyze(len_coil=el)['Ls_eff'] for el in lens]
    qs = [ind.analyze(len_coil=el)['Q_eff'] for el in lens]

    if 0:
        inds = []

        for el in lens:
            ind.len_coil = el
            inds.append(ind.sensitivity('len_coil'))

    figure()
    plot(lens/1e-3, inds)

    figure()
    plot(lens/1e-3, qs)

    figure()
    plot(inds, qs)

    show()



if __name__ == '__main__':
    main3()