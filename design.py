import numpy as np

char            = dict()
char['width']   = 0.647e-6
char['lengths'] = np.arange(200, 400, 100) * 1e-9

specs       = dict()
vdd         = specs['VDD']                  = 1.2
fu          = specs['Unity Gain Frequency'] = 1e7
cl          = specs['Load Capacitance']     = 1e-12
vstar       = specs['V*']                   = 120e-3
gm          = specs['Transconductance']     = 2 * np.pi * fu * cl
ibias_tweak = specs['Bias Current Tweak']   = 1
ibias       = specs['Bias Current']         = gm * vstar / 2.0 * ibias_tweak

verify   = dict()
wm       = verify['Active Load Width']           = 5e-6
lm       = verify['Active Load Length']          = 500e-9
cmi_xlim = verify['Common Mode Input View Span'] = (0.44, 0.46)
cmi      = verify['Common Mode Input Voltage']   = 0.447
swi      = verify['Input Voltage Half-Swing']    = 0.0021
f        = verify['Input Frequency']             = 1
wl_pair  = verify['W/L Design Pair']             = 1
