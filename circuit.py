#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import cPickle as pickle
from subprocess import PIPE

class Circuit(object):
    def __init__(self, netlist):
        self.netlist = netlist
        self.data_filename_prefix = self.netlist.split('.')[0].lower()
        self.database = dict()
        self.pkl = '{0}.pkl'.format(self.data_filename_prefix)

    def y_of_x(self, x, x_array, y_array):
        order = x_array.argsort()
        y = np.interp(x, x_array[order], y_array[order])
        return y

    def length_key(self, length):
        return '{0:.0f}n'.format(length * 1e9)

    def simulate(self, **ckt_params):
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template(self.netlist)
        filename = 'simulate.sp'

        length = ckt_params['length']
        self.database[self.length_key(length)] = dict()
        self.database[self.length_key(length)]['length'] = length
        ckt_params['data_filename'] = '{0}_{1:.0f}n'.format(self.data_filename_prefix, length * 1e9)
        with open(filename, 'w') as simulation_netlist:
            s = template.render(ckt_params)
            simulation_netlist.write(s)

        subprocess.call(['ngspice', '-b', filename], stdout=PIPE, stderr=PIPE)
        #subprocess.call(['ngspice', '-b', filename])

    def write(self):
        with open(self.pkl, 'w') as outfile:
            pickle.dump(self.database, outfile)

class Characterization(Circuit):
    def gather(self, length, vstar_spec, ibias, cm_input):
        length_key = self.length_key(length)
        f = '{0}_{1}.data'.format(self.data_filename_prefix, length_key)
        raw = np.loadtxt(f)
        width = self.database[length_key]['width'] = raw[:,1][0] #
        vgs   = self.database[length_key]['vgs']   = raw[:,3]
        vds   = self.database[length_key]['vds']   = raw[:,5]
        vth   = self.database[length_key]['vth']   = raw[:,7]
        ids   = self.database[length_key]['id']    = raw[:,9]
        gm    = self.database[length_key]['gm']    = raw[:,11]
        gds   = self.database[length_key]['gds']   = raw[:,13]
        cgs   = self.database[length_key]['cgs']   = raw[:,15]
        cgb   = self.database[length_key]['cgb']   = raw[:,17]
        cgd   = self.database[length_key]['cgd']   = raw[:,19]

        ft     = self.database[length_key]['ft']     = -gm / (2 * np.pi * (cgs + cgb + cgd))
        gmid   = self.database[length_key]['gmid']   = gm / ids
        ftgmid = self.database[length_key]['ftgmid'] = ft * gmid
        vstar  = self.database[length_key]['vstar']  = 2 / gmid
        vod    = self.database[length_key]['vod']    = vgs - vth

        self.database[length_key]['vstar_spec'] = vstar_spec
        self.database[length_key]['ibias']      = ibias

        # Compute width
        x_array = vstar
        y_array = ids
        ibias_lookup = self.y_of_x(vstar_spec, x_array, y_array)
        self.database[length_key]['width'] = width * (ibias / ibias_lookup)

        # Compute vod
        x_array = vgs
        y_array = vod
        self.database[length_key]['vod_cmi'] = self.y_of_x(cm_input, x_array, y_array)

    def plot_ftgmid_vstar(self, fig, subplot, lengths):
        # Circuit CHAR ftgmid vs vstar
        fig.add_subplot(*subplot)
        with open(self.pkl) as infile:
            database = pickle.load(infile)
        for l in lengths:
            length_key = '{0:.0f}n'.format(l * 1e9)
            x = database[length_key]['vstar']
            y = database[length_key]['ftgmid']
            plt.plot(x * 1e3, y * 1e-12, label=length_key)

        vstar_spec = database[length_key]['vstar_spec'] * 1e3
        plt.axvline(vstar_spec, color='k')
        plt.grid()
        plt.xlim(0, 400)
        plt.title('Figure of merit')
        plt.xlabel(r'Sizing, $V^*$ [mV]')
        plt.ylabel(r'$f_t\frac{g_m}{I_D}$ [$\frac{\mathrm{THz}}{\mathrm{V}}$]')
        plt.legend(loc='upper right')

    def plot_id_vstar(self, fig, subplot, lengths):
        # Circuit A id vs vstar
        fig.add_subplot(*subplot)
        with open(self.pkl) as infile:
            database = pickle.load(infile)
        for l in lengths:
            length_key = '{0:.0f}n'.format(l * 1e9)
            x = database[length_key]['vstar']
            y = database[length_key]['id']
            width = '{0:.0f}n'.format(database[length_key]['width'] * 1e9)
            label = 'W/L = ' + width + ' / ' + length_key
            plt.plot(x * 1e3, y * 1e6, label=label)

        ibias = database[length_key]['ibias']
        vstar_spec = database[length_key]['vstar_spec'] * 1e3
        plt.axvline(vstar_spec, color='k')
        plt.grid()
        plt.xlim(vstar_spec - 20, vstar_spec + 20)
        plt.ylim(0, 20.001)
        plt.title(u'Drain current, $I_D = {0:.2f}$ µA'.format(ibias * 1e6))
        plt.xlabel(r'Sizing, $V^*$ [mV]')
        plt.ylabel(u'Drain current, $I_D$ [µA]')
        plt.legend(loc='upper left')

    def plot_ftgmid_vod(self, fig, subplot, lengths):
        # Circuit CHAR ftgmid vs vod
        fig.add_subplot(*subplot)
        with open(self.pkl) as infile:
            database = pickle.load(infile)
        for l in lengths:
            length_key = '{0:.0f}n'.format(l * 1e9)
            x = database[length_key]['vod']
            y = database[length_key]['ftgmid']
            plt.plot(x * 1e3, y * 1e-12, label=length_key)

        vod_cmi = database[length_key]['vod_cmi'] * 1e3
        plt.axvline(vod_cmi, color='k')
        plt.grid()
        plt.xlim(-400, 400)
        plt.title('Figure of merit')
        plt.xlabel(r'Overdrive voltage, $V_{od}$ [V]')
        plt.ylabel(r'$f_t\frac{g_m}{I_D}$ [$\frac{\mathrm{THz}}{\mathrm{V}}$]')
        plt.legend(loc='upper left')

    def get_width(self, length):
        length_key = self.length_key(length)
        return self.database[length_key]['width']

class Verification(Circuit):
    def gather(self, length, cm_input, swing):
        length_key = self.length_key(length)
        f = '{0}_{1}.data'.format(self.data_filename_prefix, length_key)
        raw = np.loadtxt(f)
        self.database[length_key]['gate']  = raw[:,1]
        self.database[length_key]['drain'] = raw[:,3]
        self.database[length_key]['id']    = raw[:,5]
        self.database[length_key]['gain']  = raw[:,7]
        self.database[length_key]['cmi']   = cm_input
        self.database[length_key]['swing'] = swing

    def plot_gate_drain(self, fig, subplot, lengths):
        # Circuit VER gate vs drain
        fig.add_subplot(*subplot)
        with open(self.pkl) as infile:
            database = pickle.load(infile)
        for l in lengths:
            length_key = '{0:.0f}n'.format(l * 1e9)
            x = database[length_key]['gate']
            y = database[length_key]['drain']
            plt.plot(x, y, label=length_key)

        cmi = database[length_key]['cmi']
        sw  = database[length_key]['swing']
        plt.axvline(cmi, color='k')
        plt.axvspan(cmi-sw, cmi+sw, color='k', alpha=0.1)
        plt.grid()
        plt.title('DC Transfer Characteristic')
        plt.xlabel(r'Gate voltage, $V_{GS}$ [V]')
        plt.ylabel(r'Drain voltage, $V_{DS}$ [V]')
        plt.legend(loc='upper right')

    def plot_gain_gate(self, fig, subplot, lengths, cmi_xlim):
        # Circuit VER gain vs gate
        fig.add_subplot(*subplot)
        with open(self.pkl) as infile:
            database = pickle.load(infile)
        for l in lengths:
            length_key = '{0:.0f}n'.format(l * 1e9)
            x = database[length_key]['gate']
            y = database[length_key]['gain']
            plt.plot(x, y, label=length_key)

        cmi = database[length_key]['cmi']
        sw  = database[length_key]['swing']
        plt.axvline(cmi, color='k')
        plt.axvspan(cmi-sw, cmi+sw, color='k', alpha=0.1)
        plt.grid()
        plt.xlim(*cmi_xlim)
        plt.title('Gain')
        plt.xlabel(r'Gate voltage, $V_{GS}$ [V]')
        plt.ylabel(r'Gain, $a_{v}$')
        plt.legend(loc='upper right')

    def plot_gain_drain(self, fig, subplot, lengths, cmo, swo_min, swo_max):
        # Circuit VER gain vs drain
        fig.add_subplot(*subplot)
        with open(self.pkl) as infile:
            database = pickle.load(infile)
        for l in lengths:
            length_key = '{0:.0f}n'.format(l * 1e9)
            x = database[length_key]['drain']
            y = database[length_key]['gain']
            plt.plot(x, y, label=length_key)

        plt.axvline(cmo, color='k')
        plt.axvspan(swo_min, swo_max, color='k', alpha=0.1)
        plt.grid()
        plt.title('Gain')
        plt.xlabel(r'Drain voltage, $V_{DS}$ [V]')
        plt.ylabel(r'Gain, $a_{v}$')
        plt.legend(loc='upper right')

class Transient(Circuit):
    def gather(self, vdd):
        length_key = self.database.keys()[0]
        f = '{0}_{1}.data'.format(self.data_filename_prefix, length_key)
        raw = np.loadtxt(f)
        self.database[length_key]['time']  = raw[:,0]
        self.database[length_key]['gate']  = raw[:,1]
        self.database[length_key]['drain'] = raw[:,3]
        self.database[length_key]['vdd']   = vdd

    def plot_transient(self, fig, subplot):
        # Circuit TRAN
        fig.add_subplot(*subplot)
        with open(self.pkl) as infile:
            database = pickle.load(infile)
        length_key = database.keys()[0]
        x = database[length_key]['time']
        yo = database[length_key]['drain']
        yi = database[length_key]['gate']
        plt.plot(x, yo, label='Output')
        plt.plot(x, yi, label='Input')

        vdd = database[length_key]['vdd']
        plt.ylim(0, vdd + 0.001)
        plt.grid()
        plt.xlabel(r'Time, $t$ [s]')
        plt.ylabel(r'Voltage, $V$ [V]')
        plt.legend(loc='upper right')

        cmi = yi.mean()
        cmi_min = yi.min()
        cmi_max = yi.max()
        swi = cmi_max - cmi_min
        cmo = yo.mean()
        cmo_min = yo.min()
        cmo_max = yo.max()
        swo = cmo_max - cmo_min

        s = r'$v_{{ipp}} = {0:.0f}$ mV, $v_{{opp}} = {1:.0f}$ mV'.format(swi * 1e3, swo * 1e3)
        plt.title('Transient Response, ' + s)

        return [cmo, cmo_min, cmo_max]

class Frequency(Circuit):
    def gather(self, vdd):
        length_key = self.database.keys()[0]
        f = '{0}_{1}.data'.format(self.data_filename_prefix, length_key)
        raw = np.loadtxt(f)
        freq  = self.database[length_key]['freq']  = raw[:,0]
        gain  = self.database[length_key]['gain']  = raw[:,1]
        phase = self.database[length_key]['phase'] = raw[:,3] * 180 / np.pi

        ft   = self.database[length_key]['ft'] = self.y_of_x(0, gain, freq)
        phft = self.database[length_key]['phft'] = self.y_of_x(0, phase, freq)

    def plot_gain(self, fig, subplot):
        # Circuit FREQ gain
        fig.add_subplot(*subplot)
        with open(self.pkl) as infile:
            database = pickle.load(infile)
        length_key = database.keys()[0]
        x = database[length_key]['freq']
        y = database[length_key]['gain']
        plt.plot(x, y)

        ft   = database[length_key]['ft']
        phft = database[length_key]['phft']
        plt.axvspan(ft, phft, color='k', alpha=0.1)
        plt.grid()
        plt.xscale('log')
        plt.title('Gain Frequency Response')
        plt.xlabel(r'Frequency, $f$ [Hz]')
        plt.ylabel(r'Gain, $a_v$ [dB]')

    def plot_phase(self, fig, subplot):
        # Circuit FREQ phase
        fig.add_subplot(*subplot)
        with open(self.pkl) as infile:
            database = pickle.load(infile)
        length_key = database.keys()[0]
        x = database[length_key]['freq']
        y = database[length_key]['phase']
        plt.plot(x, y)

        ft   = database[length_key]['ft']
        phft = database[length_key]['phft']
        plt.axvspan(ft, phft, color='k', alpha=0.1)
        plt.grid()
        plt.xscale('log')
        plt.ylim(-45, 225)
        plt.yticks(np.array([-45, 0, 45, 90, 135, 180, 225]))
        plt.title('Phase Frequency Response')
        plt.xlabel(r'Frequency, $f$ [Hz]')
        plt.ylabel(u'Phase, $\phi$ [°]')
