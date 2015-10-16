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

import ADC

if __name__ == '__main__':
    # Grab options from the command line
    parser = argparse.ArgumentParser()
    adcget = parser.add_mutually_exclusive_group()
    parser.add_argument('-I', '--ip-roach', dest='roach', required=True,
                        help='Hostname/ip address of the ROACH.')
    adcget.add_argument('-i', '--iadc', action='store_true',
                        help='Run the iADC capture design.')
    adcget.add_argument('-q', '--quadadc', action='store_true',
                        help='Run the QuadADC capture design.')
    adcget.add_argument('-a', '--adc16', action='store_true',
                        help='Run the ADC16 capture design.')
    adcget.add_argument('-s', '--snap', action='store_true',
                        help='Run the SNAP ADC capture design')
    adcget.add_argument('-k', '--kill', action='store_true',
                        help='Kill the BOF process on the FPGA.')
    args = parser.parse_args()

    # Connect to the ROACH board and grab data.
    roach = ADC.ADC(args.roach)
    roach.check_connected()
    if args.kill:
        print 'Killing BOF process.'
        roach.progdev('')
    else:
        print 'Initializing the ADC.'
        roach.set_model([args.iadc, args.quadadc, args.adc16, args.snap])
        sys.exit(roach.start_bof())
