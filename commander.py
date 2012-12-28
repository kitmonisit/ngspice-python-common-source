#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from circuit import CurrentMirror
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import subprocess
import warnings
warnings.simplefilter('ignore')

# Characterization
p_width1 = p_width2 = 10e-6
n_width1 = 5e-6
n_width2 = 2 * n_width1
p_lengths = np.linspace(200, 500, 4) * 1e-9
n_lengths = np.arange(200, 600, 100) * 1e-9

# Specifications
vdd = 1.2
ibias = 2.83e-6

cktN = CurrentMirror(netlist='cktN.sp')
cktP = CurrentMirror(netlist='cktP.sp')

def simulate():
    subprocess.call('rm *.data', shell=True)

    cktN_params = dict()
    cktN_params['vdd']          = vdd
    cktN_params['bias_current'] = ibias
    cktN_params['width1']       = n_width1
    cktN_params['width2']       = n_width2
    for l in n_lengths:
        cktN_params['length'] = l
        cktN.simulate(**cktN_params)
        cktN.gather(l)
        cktN.write()

    cktP_params = dict()
    cktP_params['vdd']          = vdd
    cktP_params['bias_current'] = ibias
    cktP_params['width1']       = p_width1
    cktP_params['width2']       = p_width2
    for l in p_lengths:
        cktP_params['length'] = l
        cktP.simulate(**cktP_params)
        cktP.gather(l)
        cktP.write()

def plot():
    pp = PdfPages('plot.pdf')
    fig = plt.figure(figsize=(8, 6))

    cktN.plot_ro(fig=fig, subplot=(2, 2, 1), lengths=n_lengths)
    cktN.plot_id(fig=fig, subplot=(2, 2, 3), lengths=n_lengths, ibias=ibias)
    cktP.plot_ro(fig=fig, subplot=(2, 2, 2), lengths=p_lengths)
    cktP.plot_id(fig=fig, subplot=(2, 2, 4), lengths=p_lengths, ibias=ibias)

    plt.tight_layout()
    plt.savefig(pp, format='pdf')
    pp.close()

simulate()
plot()
