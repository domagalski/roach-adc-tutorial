#!/usr/bin/env python2.7

################################################################################
## This module defines a class for interfacing with basic ADC readers.
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

import os         as _os
import sys        as _sys
import time       as _time
import numpy      as _np
import subprocess as _spr
from corr import katcp_wrapper as _katcp

BRAM_SIZE = 4 << 11
DELAY     = 0.001

BOF_IADC = 'iadc_demux4.bof'
BOF_QUAD = 'adc8.bof'
BOF_ADC2 = 'adc32.bof'
BOF_SNAP = 'snap_adc.bof'

ADC_INIT = 'adc16_init.rb'
RB_ADC2 = _os.path.join('/usr/local/bin', ADC_INIT)
RB_SNAP = _os.path.join(_os.environ['HOME'], 'jasper_devel/snap_adc/ruby/bin')
RB_SNAP = _os.path.join(RB_SNAP, ADC_INIT)

class ADC(_katcp.FpgaClient):
    """
    ADC class for communicating with a ROACH board.
    """
    def __init__(self, *args, **kwargs):
        """
        Create the ROACH object and store the model type.
        """
        _katcp.FpgaClient.__init__(self, *args, **kwargs)

        self.model = None
        self.antennas = None
        self.board = 'FPGA'

    def check_connected(self, timeout=10):
            """
            This function checks if the ROACH is connected, and raises an
            IOError if the client can't reach the ROACH.
            Input:
            - ``timeout``: The amount of seconds to wait before IOError.
            """
            if not self.wait_connected(timeout):
                raise IOError('Cannot connect.')

    def get_ant_name(self, ant_num):
        """
        Get the antenna name that the ROACH uses.
        """
        if self.model == 1:
            register = 'dout'
        else:
            register = 'ant_'
        if self.model <= 2:
            register += str(ant_num)
        else:
            register += chr(ord('a') + ant_num / 4) + str(ant_num % 4 + 1)
        return register

    def read_antenna(self, ant_num):
        """
        This function reads data from a BRAM for an antenna.
        """
        register = self.get_ant_name(ant_num)
        if self.model == 1:
            bram_size = BRAM_SIZE/2
        else:
            bram_size = BRAM_SIZE
        bram_bits = _np.fromstring(self.read(register, bram_size), '>u4')
        return bram_bits.astype(_np.int8)

    def retrieve_data(self, filename=None):
        """
        This function retrieves data from the ROACH and either saves it
        to an npz file or returns it if the filename is not given.
        """
        # Read the data from the ROACH
        ant_names = map(self.get_ant_name, range(self.antennas))
        ant_data  = map(self.read_antenna, range(self.antennas))
        antennas  = dict(zip(ant_names, ant_data))

        # Save data to a file, or return it.
        if filename:
            _np.savez(filename, **antennas)
        else:
            return antennas

    def set_model(self, model_params=[0,0,0,0]):
        """
        This function sets the ROACH model
        """
        # Check validity of options
        if sum(model_params) != 1:
            raise ValueError('Invalid options.')

        # Model numbers.
        # 1: iADC
        # 2: QuadADC
        # 4: ADC16
        # 8: SNAP
        self.model = sum([n << i for i, n in enumerate(model_params)])
        if self.model == 1:
            self.antennas = 8
            self.adc_bof = BOF_IADC
            self.board = 'ROACH'
        elif self.model == 2:
            self.antennas = 8
            self.adc_bof = BOF_QUAD
            self.board = 'ROACH'
        elif self.model == 4:
            self.antennas = 32
            self.adc_bof = BOF_ADC2
            self.board = 'ROACH2'
        elif self.model == 8:
            self.antennas = 12
            self.adc_bof = BOF_SNAP
            self.board = 'SNAP board'

    def start_bof(self, delay=DELAY):
        """
        Start the bof file on the ROACH.
        """
        self.progdev('')
        adc_init = None

        # ROACH ADC's don't need a calibration script.
        if self.model <= 2:
            self.progdev(self.adc_bof)
            _time.sleep(delay)
            return 0

        # Run a calibration script to start the ADC
        elif self.model == 4:
            adc_init = RB_ADC2
        elif self.model == 8:
            adc_init = RB_SNAP
        status = _os.system(' '.join([adc_init, self.host, self.adc_bof]))

        _time.sleep(delay)
        return status

    def store_data(self, delay=DELAY):
        """
        This function stores data into the ROACH's BRAM.
        """
        self.write_int('trig', 1)
        self.write_int('trig', 0)
        while not self.read_int('capture'):
            _time.sleep(delay)
