# -*- coding: utf-8 -*-

import threading
import cflib.crtp
import time

from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander

# URI to the Crazyflie to connect to
drogni = [
        # 'radio://0/80/2M/E7E7E7E7E0',
        # 'radio://0/80/2M/E7E7E7E7E1',
        'radio://0/80/2M/E7E7E7E7E2',
        # 'radio://0/80/2M/E7E7E7E7E3',
        # 'radio://0/80/2M/E7E7E7E7E4',
        # 'radio://0/80/2M/E7E7E7E7E5',
        # 'radio://0/80/2M/E7E7E7E7E6',
        # 'radio://0/80/2M/E7E7E7E7E7',
        # 'radio://0/80/2M/E7E7E7E7E8'
        # 'radio://0/80/2M/E7E7E7E7E9',
        ]

SPACING = 0.25


def slightly_more_complex_usage():
    with SyncCrazyflie(drogni, cf=Crazyflie(rw_cache='./cache')) as scf:
        with PositionHlCommander(
                scf,
                x=0.0, y=0.0, z=0.0,
                default_velocity=0.3,
                default_height=0.5,
                controller=PositionHlCommander.CONTROLLER_MELLINGER) as pc:
            # Go to a coordinate
            pc.go_to(1.0, 1.0, 1.0)

            # Move relative to the current position
            pc.right(1.0)

            # Go to a coordinate and use default height
            pc.go_to(0.0, 0.0)

            # Go slowly to a coordinate
            pc.go_to(1.0, 1.0, velocity=0.2)

            # Set new default velocity and height
            pc.set_default_velocity(0.3)
            pc.set_default_height(1.0)
            pc.go_to(0.0, 0.0)


def simple_sequence():
    indice = 0.0

    for flaio in drogni:
        indice += 1
        relativeSpacing = SPACING * indice
        
        def daje():
            with SyncCrazyflie(flaio, cf=Crazyflie(rw_cache='./cache')) as scf:
                with PositionHlCommander(scf) as pc:
                    cf = scf.cf
                    # Set black color effect
                    # cf.param.set_value('ring.effect', '0')
                    # cf.param.set_value('ring.effect', '14')
                    # cf.param.set_value('ring.fadeTime', '1.0')
                    # time.sleep(1)

                    # pc.forward(1.0)
                    # pc.left(1.0)
                    # pc.back(1.0)
                    input('ready, press a key')
                    pc.go_to(0.0, 0.0, 1)
                    print('1')
            
                    pc.go_to(0.0, 1+relativeSpacing, 1)
                    print('2')
                    time.sleep(1)

                    cf.param.set_value('ring.fadeColor', '0x008080')
                    pc.go_to(1+relativeSpacing, 1+relativeSpacing, 1)
                    print('3')
                    time.sleep(1)

                    cf.param.set_value('ring.fadeColor', '0x307070')
                    pc.go_to(1.0+relativeSpacing, 0.0+relativeSpacing, 1)
                    print('4')
                    time.sleep(2)
                    
                    pc.go_to(0.0+relativeSpacing, 0.0+relativeSpacing, 1)
                    print('end')
                    # cf.param.set_value('ring.fadeColor', '0x307070')
                    # pc.go_to(0.0, 0.0, 1.3)
                    # print('5')
                    # time.sleep(2)

                    # cf.param.set_value('ring.fadeColor', '0xFFFFFF')
                    # cf.param.set_value('ring.fadeColor', '0xFF00FF')
                    # cf.param.set_value('ring.fadeColor', '0xFF0000')
                    # cf.param.set_value('ring.fadeColor', '0x000000')
                    # print('6')
                    # cf.param.set_value('ring.fadeColor', '0x6060A0')
                    def antani():
                        print ('antani')
        t= threading.Thread(target=daje)
        t.start()

if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)

    simple_sequence()
    # slightly_more_complex_usage()






#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2018 Bitcraze AB
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
This script shows the basic use of the PositionHlCommander class.

Simple example that connects to the crazyflie at `URI` and runs a
sequence. This script requires some kind of location system.

The PositionHlCommander uses position setpoints.

Change the URI variable to your Crazyflie configuration.
"""