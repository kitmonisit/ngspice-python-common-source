#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from circuit import Characterization, Verification, Transient, Frequency
import design
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import subprocess
import warnings
warnings.simplefilter('ignore')

# Characterization
width_char = design.char['width']
lengths    = design.char['lengths']
widths     = []

# Specifications
vdd         = design.specs['VDD']
fu          = design.specs['Unity Gain Frequency']
cl          = design.specs['Load Capacitance']
vstar       = design.specs['V*']
gm          = design.specs['Transconductance']
ibias_tweak = design.specs['Bias Current Tweak']
ibias       = design.specs['Bias Current']

# Verification
wm       = design.verify['Active Load Width']
lm       = design.verify['Active Load Length']
cmi_xlim = design.verify['Common Mode Input View Span']# = (0.27, 0.29)
cmi      = design.verify['Common Mode Input Voltage']# = 0.2835
swi      = design.verify['Input Voltage Half-Swing']
f        = design.verify['Input Frequency']
wl_pair  = design.verify['W/L Design Pair']

cktCHAR = Characterization(netlist='cktCHAR.sp')
cktVER = Verification(netlist='cktVEr.sp')
cktTRAN = Transient(netlist='cktTRAN.sp')
cktFREQ = Frequency(netlist='cktFREQ.sp')

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
        cktVER.gather(length=l, cm_input=cmi, swing=swi)
        cktVER.write()

    design_w, design_l = WL_pairs[wl_pair]

    cktTRAN_params = dict()
    cktTRAN_params['vdd']              = vdd
    cktTRAN_params['bias_current']     = ibias
    cktTRAN_params['cm_input']         = cmi
    cktTRAN_params['swing']            = swi
    cktTRAN_params['freq']             = f
    cktTRAN_params['stop_time']        = 5.0 / f
    cktTRAN_params['step']             = cktTRAN_params['stop_time'] / 2000.0
    cktTRAN_params['width_mirror']     = wm
    cktTRAN_params['length_mirror']    = lm
    cktTRAN_params['load_capacitance'] = cl
    cktTRAN_params['width']            = design_w
    cktTRAN_params['length']           = design_l
    cktTRAN.simulate(**cktTRAN_params)
    cktTRAN.gather(vdd=vdd)
    cktTRAN.write()

    cktFREQ_params = dict()
    cktFREQ_params['vdd']              = vdd
    cktFREQ_params['bias_current']     = ibias
    cktFREQ_params['cm_input']         = cmi
    cktFREQ_params['swing']            = swi
    cktFREQ_params['freq']             = f
    cktFREQ_params['width_mirror']     = wm
    cktFREQ_params['length_mirror']    = lm
    cktFREQ_params['load_capacitance'] = cl
    cktFREQ_params['width']            = design_w
    cktFREQ_params['length']           = design_l
    cktFREQ.simulate(**cktFREQ_params)
    cktFREQ.gather(vdd=vdd)
    cktFREQ.write()

def plot():
    pp = PdfPages('plot.pdf')
    fig = plt.figure(figsize=(16, 10))

    cktCHAR.plot_ftgmid_vstar(fig, (3, 3, 1), lengths=lengths)
    cktCHAR.plot_id_vstar(fig, (3, 3, 2), lengths=lengths)
    cktCHAR.plot_ftgmid_vod(fig, (3, 3, 3), lengths=lengths)
    cktVER.plot_gate_drain(fig, (3, 3, 4), lengths=lengths)
    cktVER.plot_gain_gate(fig, (3, 3, 5), lengths=lengths, cmi_xlim=cmi_xlim)
    cmo, swo_min, swo_max = cktTRAN.plot_transient(fig, (3, 3, 7))
    cktVER.plot_gain_drain(fig, (3, 3, 6), lengths=lengths, cmo=cmo, swo_min=swo_min, swo_max=swo_max)
    cktFREQ.plot_gain(fig, (3, 3, 8))
    cktFREQ.plot_phase(fig, (3, 3, 9))

    plt.tight_layout()
    plt.savefig(pp, format='pdf')
    pp.close()

simulate()
plot()
