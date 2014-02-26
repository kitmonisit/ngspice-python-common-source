import numpy as np

char            = dict()
char['width']   = 1e-6
char['lengths'] = np.arange(200, 500, 100) * 1e-9

specs       = dict()
vdd         = specs['VDD']                  = 1.2
fu          = specs['Unity Gain Frequency'] = 1e9
cl          = specs['Load Capacitance']     = 1e-12
vstar       = specs['V*']                   = 150e-3
gm          = specs['Transconductance']     = 2 * np.pi * fu * cl
ibias_tweak = specs['Bias Current Tweak']   = 1
ibias       = specs['Bias Current']         = gm * vstar / 2.0 * ibias_tweak

verify   = dict()
wm       = verify['Active Load Width']           = 5e-6
lm       = verify['Active Load Length']          = 500e-9
cmi      = verify['Common Mode Input Voltage']   = 0.495 #0.4475
cmi_span = (cmi - 0.03, cmi + 0.03)
cmi_xlim = verify['Common Mode Input View Span'] = cmi_span
swi      = verify['Input Voltage Half-Swing']    = 0.005 #0.0025
f        = verify['Input Frequency']             = 1e3
wl_pair  = verify['W/L Design Pair']             = 2
