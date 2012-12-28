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
        plt.ylim(0, 50.001)
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

    def plot_gain_drain(self, fig, subplot, lengths):
        # Circuit VER gain vs drain
        fig.add_subplot(*subplot)
        with open(self.pkl) as infile:
            database = pickle.load(infile)
        for l in lengths:
            length_key = '{0:.0f}n'.format(l * 1e9)
            x = database[length_key]['drain']
            y = database[length_key]['gain']
            plt.plot(x, y, label=length_key)

        plt.grid()
        plt.title('Gain')
        plt.xlabel(r'Drain voltage, $V_{DS}$ [V]')
        plt.ylabel(r'Gain, $a_{v}$')
        plt.legend(loc='upper right')
