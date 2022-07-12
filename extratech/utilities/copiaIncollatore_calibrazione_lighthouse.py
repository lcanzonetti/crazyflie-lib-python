# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2019 Bitcraze AB
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.
"""
Example of how to read the Lighthouse base station geometry and
calibration memory from a Crazyflie
"""
import logging, time
from threading import Event

import cflib.crtp  # noqa
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.mem import LighthouseMemHelper
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
import stenBaiatore
import wakeUppatore


# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

source_uri = 'radio://0/80/2M/E7E7E7E7E0'

destination_uris = [    
        # 'radio://0/80/2M/E7E7E7E7E0',
        'radio://0/80/2M/E7E7E7E7E1',
        # 'radio://0/80/2M/E7E7E7E7E2',
        # 'radio://1/90/2M/E7E7E7E7E3',
        # 'radio://1/90/2M/E7E7E7E7E4',
        # 'radio://1/90/2M/E7E7E7E7E5',
        # 'radio://2/100/2M/E7E7E7E7E6',
        # 'radio://2/100/2M/E7E7E7E7E7',
        # 'radio://2/100/2M/E7E7E7E7E8'
        # 'radio://2/110/2M/E7E7E7E7E9',
        # 'radio://0/110/2M/E7E7E7E7EA',
        ]


geo      = None
calib    = None

class ReadMem:
    def __init__(self, uri):
        self._event = Event()

        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            helper = LighthouseMemHelper(scf.cf)
            helper.read_all_geos(self._geo_read_ready)
            self._event.wait()
            self._event.clear()
            helper.read_all_calibs(self._calib_read_ready)
            self._event.wait()

    def _geo_read_ready(self, geo_data):
        global geo
        print('---- Retreived geometry for base stations:')
        print (geo_data)
        self._event.set()

    def _calib_read_ready(self, calib_data):
        global calib
        print('---- Retreived geometry for base stations:')
        print (calib_data)
        self._event.set()

class WriteMem:
    def __init__(self, uro, geo_dict, calib_dict):
        self._event = Event()
        self.uro = uro

        with SyncCrazyflie(self.uro,  cf=Crazyflie(rw_cache='./cache')) as scf:
            helper = LighthouseMemHelper(scf.cf)
            helper.write_geos(geo_dict, self._data_written)
            self._event.wait()
            self._event.clear()
            
            helper.write_calibs(calib_dict, self._data_written)
            self._event.wait()

    def _data_written(self, success):
        if success:
            print('Data written on %s' % self.uro)
        else:
            print('Write failed on %s' % self.uro)

        self._event.set()



if __name__ == '__main__':
    cflib.crtp.init_drivers()
    wakeUppatore.wakeUpSingle(source_uri)
    time.sleep(3)

    ReadMem(source_uri)
    stenBaiatore.standBySingle(source_uri)
    for uro in destination_uris:
        wakeUppatore.wakeUpSingle(uro)
        time.sleep(3)
        print('writing on %s'% uro)
        WriteMem(uro, geo, calib)
        stenBaiatore.standBySingle(uro)



