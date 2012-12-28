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

    def write(self):
        with open(self.pkl, 'w') as outfile:
            pickle.dump(self.database, outfile)

class CurrentMirror(Circuit):
    def gather(self, length):
        length_key = self.length_key(length)
        f = '{0}_{1}.data'.format(self.data_filename_prefix, length_key)
        raw = np.loadtxt(f)

        vvo = self.database[length_key]['vvo'] = raw[:,1]
        ids = self.database[length_key]['id']  = raw[:,3]
        gds = self.database[length_key]['gds'] = raw[:,5]
        vds = self.database[length_key]['vds'] = raw[:,7]

        self.database[length_key]['ro'] = 1 / gds

    def plot_ro(self, fig, subplot, lengths):
        # Circuit A ro
        fig.add_subplot(*subplot)
        with open(self.pkl) as infile:
            database = pickle.load(infile)
        for l in lengths:
            length_key = '{0:.0f}n'.format(l * 1e9)
            x = database[length_key]['vvo']
            y = database[length_key]['ro']
            plt.plot(x, y * 1e-6, label=length_key)
        plt.grid()
        plt.title('Output resistance')
        plt.xlabel(r'Output voltage, $V_o$ [V]')
        plt.ylabel(r'Output resistance, $r_o$ [M$\Omega$]')
        plt.legend(loc='lower left')

    def plot_id(self, fig, subplot, lengths, ibias):
        # Circuit A id
        fig.add_subplot(*subplot)
        with open(self.pkl) as infile:
            database = pickle.load(infile)
        for l in lengths:
            length_key = '{0:.0f}n'.format(l * 1e9)
            x = database[length_key]['vvo']
            y = database[length_key]['id']
            #width = u'{0:.0f}µm'.format(database[length_key]['width'] * 1e6)
            #label = 'W/L = ' + width + '/' + length_key
            #plt.plot(x, y * 1e6, label=label)
            plt.plot(x, y * 1e6)
        plt.grid()
        plt.title(u'Drain current, $I_D = {0:.2f}$ µA'.format(ibias * 1e6))
        plt.xlabel(r'Output voltage, $V_o$ [V]')
        plt.ylabel(u'Drain current, $I_D$ [µA]')
        plt.legend(loc='lower left')
