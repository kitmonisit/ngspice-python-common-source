#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from circuit import Characterization, Verification
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import subprocess
import warnings
warnings.simplefilter('ignore')

# Characterization
width_char = 0.647e-6
lengths = np.arange(200, 400, 100) * 1e-9
widths = []

# Specifications
vdd = 1.2
fu = 1e7
cl = 1e-12
vstar = 120e-3
gm = 2 * np.pi * fu * cl
ibias_tweak = 1
ibias = gm * vstar / 2.0 * ibias_tweak

# Verification
wm  = 5e-6
lm  = 500e-9
cmi_xlim = (0.44, 0.46)
cmi = 0.447
sw  = 0.0019
f   = 1

cktCHAR = Characterization(netlist='cktCHAR.sp')
cktVER = Verification(netlist='cktVEr.sp')

def simulate():
    subprocess.call('rm *.data', shell=True)

    cktCHAR_params = dict()
    cktCHAR_params['width'] = width_char
    for l in lengths:
        cktCHAR_params['length'] = l
        cktCHAR.simulate(**cktCHAR_params)
        cktCHAR.gather(length=l, vstar_spec=vstar, ibias=ibias, cm_input=cmi)
        cktCHAR.write()
        widths.append(cktCHAR.get_width(l))

    WL_pairs = zip(widths, lengths)

    cktVER_params = dict()
    cktVER_params['vdd']   = vdd
    cktVER_params['bias_current']     = ibias
    cktVER_params['width_mirror']     = wm
    cktVER_params['length_mirror']    = lm
    cktVER_params['load_capacitance'] = cl
    for w, l in WL_pairs:
        cktVER_params['width'] = w
        cktVER_params['length'] = l
        cktVER.simulate(**cktVER_params)
        cktVER.gather(length=l, cm_input=cmi, swing=sw)
        cktVER.write()

def plot():
    pp = PdfPages('plot.pdf')
    fig = plt.figure(figsize=(12, 6))

    cktCHAR.plot_ftgmid_vstar(fig, (2, 3, 1), lengths=lengths)
    cktCHAR.plot_id_vstar(fig, (2, 3, 2), lengths=lengths)
    cktCHAR.plot_ftgmid_vod(fig, (2, 3, 3), lengths=lengths)
    cktVER.plot_gate_drain(fig, (2, 3, 4), lengths=lengths)
    cktVER.plot_gain_gate(fig, (2, 3, 5), lengths=lengths, cmi_xlim=cmi_xlim)
    cktVER.plot_gain_drain(fig, (2, 3, 6), lengths=lengths)

    plt.tight_layout()
    plt.savefig(pp, format='pdf')
    pp.close()

simulate()
plot()
