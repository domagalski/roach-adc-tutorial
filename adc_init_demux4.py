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

from corr.katcp_wrapper import FpgaClient as ROACH

if __name__ == '__main__':
    # Grab options from the command line
    parser = argparse.ArgumentParser()
    adcget = parser.add_mutually_exclusive_group()
    parser.add_argument('-i', '--ip-roach', dest='roach', required=True,
                        help='Hostname/ip address of the ROACH.')
    adcget.add_argument('-z', '--zdok1', action='store_true',
                        help='Use the zdok 1 model instead of the zdok 0.')
    adcget.add_argument('-k', '--kill', action='store_true',
                        help='Kill the BOF process on the FPGA.')
    args = parser.parse_args()

    # Connect to the ROACH board
    roach = ROACH(args.roach)
    if not roach.wait_connected(10):
        print 'ERROR: Cannot connect to ROACH.'
        sys.exit(1)

    # Set up the FPGA
    if args.kill:
        print 'Killing BOF process.'
        roach.progdev('')
    else:
        print 'Initializing the ADC.'
        boffile = 'iadc_demux4_zdok%d.bof' % int(args.zdok1)
        roach.progdev(boffile)
