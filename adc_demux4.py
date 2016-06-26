#!/usr/bin/env python2.7

################################################################################
## This script reads the bram of an 8-input ADC
## Copyright (C) 2014  Rachel Domagalski: domagalski@berkeley.edu
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## ## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

import sys
import argparse
import struct as s
import numpy as np
from numpy import fft

import ADC

class DEMUX4(ADC.ADC):
    def read_data(self, bram_name):
        bram_size = 4 << 16
        print bram_name
        readout = np.fromstring(self.read(bram_name, bram_size), '>i1')
        print 'read.'
        return (bram_name, readout)

    def retrieve_data(self, ant_list=['adc_i', 'adc_q'], outfile=None):
        readout = dict(map(self.read_data, ant_list))
        return readout

if __name__ == '__main__':
    # Grab options from the command line
    parser = argparse.ArgumentParser()
    output = parser.add_mutually_exclusive_group()
    parser.add_argument('-i', '--ip-roach', dest='roach', required=True,
                        help='Hostname/ip address of the ROACH.')
    output.add_argument('-o', '--output-file',
                        dest='outfile',
                        help='NPZ file to save data to.')
    output.add_argument('-A', '--antennas', nargs='+',
                        help='Antennas to plot.')
    parser.add_argument('-d', '--demux', type=int, default=4,
                        help='Demux mode to use (default 4).')
    parser.add_argument('-f', '--fft', action='store_true',
                        help='Run an FFT on the data.')
    parser.add_argument('-S', '--samp-rate', default=1e7, type=float,
                        help='Samping rate of the ADC (for plots).')
    args = parser.parse_args()

    # Make sure that the user specified something to do.
    if args.outfile is None and args.antennas is None:
        print 'ERROR: Nothing to do.'
        sys.exit(1)
    if args.outfile is not None and args.fft:
        print 'ERROR: This script only stores raw data.'
        sys.exit(1)

    # Connect to the FPGA board and grab data.
    roach = DEMUX4(args.roach)
    roach.check_connected()
    roach.store_data()

    # Capture data onto the FPGA and save it
    if args.antennas is not None:
        import matplotlib.pyplot as plt

        # Read out data from the FPGA.
        antennas = ['adc_i', 'adc_q']
        readout = roach.retrieve_data(antennas)
        nsamples = len(readout['adc_i'])
        if args.fft:
            freq = fft.fftfreq(nsamples, 1e6 / args.samp_rate)[:nsamples/2]
            for ant in antennas:
                pspec = np.abs(fft.fft(readout[ant])[:nsamples/2])**2
                pspec = 10*np.log10(pspec/np.max(pspec))
                plt.figure()
                plt.plot(freq, pspec)
                plt.xlabel('Frequency (MHz)')
                plt.ylabel('Power (dB)')
                plt.title(ant)
                plt.axis([0, freq[-1], np.min(pspec), 0])
        else:
            margin = 5
            time_axis = np.arange(nsamples) / args.samp_rate * 1e6
            for ant in antennas:
                plt.figure()
                plt.plot(time_axis, readout[ant])
                min_adc = np.min(readout[ant]) - margin
                max_adc = np.max(readout[ant]) + margin
                plt.xlabel(r'Time ($\mu s$)')
                plt.title(ant)
                plt.axis([0, time_axis[-1], min_adc, max_adc])
        plt.tight_layout()
        plt.show()
    else:
        roach.retrieve_data(args.outfile)
