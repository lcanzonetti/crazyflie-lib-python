# -*- coding: utf-8 -*-

import cflib.crtp
import time

from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander

# URI to the Crazyflie to connect to
uri = 'radio://0/80/2M/E7E7E7E7E7'

def slightly_more_complex_usage():
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
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
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        with PositionHlCommander(scf) as pc:
            cf = scf.cf
            # Set black color effect
            cf.param.set_value('ring.effect', '0')
            cf.param.set_value('ring.effect', '14')
            cf.param.set_value('ring.fadeTime', '1.0')
            time.sleep(1)

            # pc.forward(1.0)
            # pc.left(1.0)
            # pc.back(1.0)
            pc.go_to(0.0, 0.3, 0.5)
            pc.go_to(0.0, 0.5, 0.7)
            pc.go_to(0.0, 0.7, 0.9)
            cf.param.set_value('ring.fadeColor', '0x0000A0')
            pc.go_to(0.0, 0.9, 1.5)
            cf.param.set_value('ring.fadeColor', '0x00A000')
            pc.go_to(0.0, 0.6, 1.3)
            cf.param.set_value('ring.fadeColor', '0xA0A000')
            pc.go_to(0.0, 0.2, 1.1)
            pc.set_default_velocity(0.9)
            pc.go_to(1.5, 0, 1.1)
            pc.go_to(-1.5, 0, 1.1)
            pc.set_default_velocity(0.3)
            cf.param.set_value('ring.fadeColor', '0x00A0A0')
            pc.go_to(0.0, -0.5, 1.0)
            cf.param.set_value('ring.fadeColor', '0x00A0A0')
            time.sleep(120)
            pc.go_to(0.0, -0.2, 0.8)
            cf.param.set_value('ring.fadeColor', '0x008080')
            pc.go_to(0.0, -0.2, 0.5)
            cf.param.set_value('ring.fadeColor', '0x307070')
            pc.go_to(0.0, 0.0, 0.5)
            cf.param.set_value('ring.fadeColor', '0x6060A0')
            def antani():
                print ('antani')


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