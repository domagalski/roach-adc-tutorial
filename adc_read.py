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
import numpy as np
from numpy import fft

import ADC


if __name__ == '__main__':
    # Grab options from the command line
    parser = argparse.ArgumentParser()
    output = parser.add_mutually_exclusive_group()
    adcget = parser.add_mutually_exclusive_group()
    parser.add_argument('-I', '--ip-roach', dest='roach', required=True,
                        help='Hostname/ip address of the ROACH.')
    output.add_argument('-o', '--output-file',
                        dest='outfile',
                        help='NPZ file to save data to.')
    output.add_argument('-A', '--antennas', nargs='+',
                        help='Antennas to plot.')
    parser.add_argument('-f', '--fft', action='store_true',
                        help='Run an FFT on the data.')
    adcget.add_argument('-i', '--iadc', action='store_true',
                        help='Run the iADC capture design.')
    adcget.add_argument('-q', '--quadadc', action='store_true',
                        help='Run the QuadADC capture design.')
    adcget.add_argument('-a', '--adc16', action='store_true',
                        help='Run the ADC16 capture design.')
    adcget.add_argument('-s', '--snap', action='store_true',
                        help='Run the SNAP ADC capture design.')
    parser.add_argument('-S', '--samp-rate', default=200e6, type=float,
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
    roach = ADC.ADC(args.roach)
    roach.set_model([args.iadc, args.quadadc, args.adc16, args.snap])
    roach.check_connected()
    roach.store_data()

    # Capture data onto the FPGA and save it
    if args.antennas is not None:
        import matplotlib.pyplot as plt

        # Read out data from the FPGA.
        antennas = sorted(args.antennas)
        readout = roach.retrieve_data()
        if roach.model == 1:
            name = lambda s: 'dout' + s
        else:
            name = lambda s: 'ant_' + s
        outdata = {ant:readout[name(ant)] for ant in antennas}

        nsamples = ADC.BRAM_SIZE / 4
        if roach.model == 1:
            nsamples /= 2
        if args.fft:
            freq = fft.fftfreq(nsamples, 1e6 / args.samp_rate)[:nsamples/2]
            for ant in antennas:
                pspec = np.abs(fft.fft(outdata[ant])[:nsamples/2])**2
                pspec = 10*np.log10(pspec/np.max(pspec))
                plt.figure()
                plt.plot(freq, pspec)
                plt.xlabel('Frequency (MHz)')
                plt.ylabel('Power (dB)')
                plt.title(name(ant))
                plt.axis([0, freq[-1], np.min(pspec), 0])
        else:
            margin = 5
            time_axis = np.arange(nsamples) / args.samp_rate * 1e6
            for ant in antennas:
                plt.figure()
                plt.plot(time_axis, outdata[ant])
                min_adc = np.min(outdata[ant]) - margin
                max_adc = np.max(outdata[ant]) + margin
                plt.xlabel(r'Time ($\mu s$)')
                plt.title(name(ant))
                plt.axis([0, time_axis[-1], min_adc, max_adc])
        plt.tight_layout()
        plt.show()
    else:
        roach.retrieve_data(args.outfile)
