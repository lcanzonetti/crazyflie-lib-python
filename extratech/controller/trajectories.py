
import time, threading
from   colorama             import Fore, Back, Style
from   colorama             import init as coloInit
coloInit(convert=True)

from   cflib.crazyflie.mem                        import Poly4D
from   cflib.crazyflie.mem                        import MemoryElement

import GLOBALS as GB



####################################################################     trst sequencesss

def land_and_clear(CF):
    CF.statoDiVolo = 'landing'
    CF.land()
    CF.statoDiVolo = 'idle'
    CF.current_sequence = None
    CF.currentSequence_killingPill.clear()

def sequenzaUno(CF):   
    def seq1():
        print('taking off')
        CF.statoDiVolo = 'taking off'
        # CF.takeOff()     
        CF.statoDiVolo = 'seq1'
        CF.setRingColor(255,   0,   0)
        time.sleep(1)
        while not CF.currentSequence_killingPill.is_set():
            print('going to 1.5 1.5 1.0 in 1 sec')
            # CF.positionHLCommander.go_to(1.5, 1.5, 1.0,1)
            CF.setRingColor(255,   0,   0)
            if CF.currentSequence_killingPill.is_set(): break
            time.sleep(1)

            print('going to 1.5 -1.5 1.0 in 1 sec')
            # CF.positionHLCommander.go_to(1.5, -1.5, 1.0,1)
            CF.setRingColor(  0, 255,  0)
            if CF.currentSequence_killingPill.is_set(): break
            time.sleep(1)

            print('going to -1.5 -1.5 1.0 in 1 sec')
            # CF.positionHLCommander.go_to(-1.50, -1.5, 1.0,1)
            CF.setRingColor(  0,  0, 255)
            if CF.currentSequence_killingPill.is_set(): break
            time.sleep(1)

            print('going to -1.5 1.5 1.0 in 1 sec')
            # CF.positionHLCommander.go_to(-1.5, 1.5, 1,1)
            if CF.currentSequence_killingPill.is_set(): break
            time.sleep(1)

            print('going to 0 0 1.5 in 1 sec')
            # CF.positionHLCommander.go_to(0,   0, 1.5,1 )


            if CF.currentSequence_killingPill.is_set(): break
            CF.setRingColor(255, 255,   0)
            time.sleep(0.5)
            CF.currentSequence_killingPill.is_set()
            CF.setRingColor(255,   0,   0)
            time.sleep(0.5)
            if CF.currentSequence_killingPill.is_set(): break
            CF.setRingColor(  0, 255,   0)
            if CF.currentSequence_killingPill.is_set(): break
            time.sleep(0.5)
            CF.setRingColor(  0,   0, 255)
            if CF.currentSequence_killingPill.is_set(): break
            time.sleep(0.5)
            CF.setRingColor  (0, 255, 255)
            if CF.currentSequence_killingPill.is_set(): break
            time.sleep(0.5)
            CF.setRingColor(255, 255,   0)
            if CF.currentSequence_killingPill.is_set(): break
            time.sleep(0.5)
            if CF.currentSequence_killingPill.is_set(): break
            CF.setRingColor(255,   0, 255)
            time.sleep(0.5)
            
        land_and_clear(CF)
        print('fine quadratone di test')
    print('Drogno: %s. Inizio quadratone di test' % CF.ID)
    threading.Thread(target=seq1, daemon=True).start()
    
#  un giro di yaw
def sequenzaDue(CF): #   blocking?
    print(Fore.LIGHTRED_EX + 'Drogno: %s. Inizio giretto sul posto' % CF.ID)
    # CF.takeOff(3.)
    while not CF.currentSequence_killingPill.is_set():
        print('giro a 90°')
        # CF._cf.high_level_commander.go_to(0.0,0.0,1.2, 90, 1)
        time.sleep(1)
        print('giro a 180°')
        # CF._cf.high_level_commander.go_to(0.0,0.0,1.2, 180, 1)
        time.sleep(1)
        if CF.currentSequence_killingPill.is_set():
            break
        print('giro a 270°')
        # CF._cf.high_level_commander.go_to(0.0,0.0,1.2, 270, 1)
        time.sleep(1)
        print('torno a 0°')
        # CF._cf.high_level_commander.go_to(0.0,0.0,1.2, 00, 1)
        time.sleep(1)
    land_and_clear(CF)
    print('fine quadratone di test')

#  un giro relativo con diametro 1.5 mt
def sequenzaTre(CF):
    print('Drogno: %s. Inizio giretto da 0.75 di test' % CF.ID)
    # CF.motionCommander.take_off(height=1.1,velocity=0.4)
    CF.statoDiVolo = 'taking off'
    # CF.motionCommander.start_circle_left(radius_m=0.7, velocity=1)
    CF.statoDiVolo = 'test 3'
    CF.currentSequence_killingPill.wait()
    land_and_clear(CF)
    print('Drogno: %s. Fine circoletto da 0.75 di test' % CF.ID)
#  un giro relativo con diametro 3 mt con il motion commander
def sequenzaQuattro(CF):
    print('Drogno: %s. Inizio giretto (seq4) da 1.5mt' % CF.ID)
    CF.statoDiVolo = 'taking off'
    # CF.motionCommander.take_off(height=1.1,velocity=0.4)
    CF.statoDiVolo = 'test 3'

    # CF.motionCommander.start_circle_left(radius_m=1.5, velocity=2)
    CF.currentSequence_killingPill.wait()
    land_and_clear(CF)

    print('Drogno: %s. Fine circoletto (seq4) da 1.5 mt' % CF.ID)
    # quadrato con il motion commander
def sequenzaCinque(CF):
        def seq5():
            CF.statoDiVolo = 'taking off'
            # CF.takeOff()     
            CF.statoDiVolo = 'seq5'
            while not CF.currentSequence_killingPill.is_set():
                print('faccio quadrati col motion commader fino a che non mi si dice il contrario')
                # CF.motionCommander.left(1.5,1.5)
                time.sleep(0.8)
                # CF.motionCommander.start_turn_left(150)
                time.sleep(0.8)
                # CF.motionCommander.stop()
                if CF.currentSequence_killingPill.is_set(): break
                time.sleep(0.8)
                # CF.motionCommander.forward(1.5,1.5)
                # CF.motionCommander.start_turn_right(150)
                if CF.currentSequence_killingPill.is_set(): break
                time.sleep(0.8)
                # CF.motionCommander.right(1.5,1.5)
                # CF.motionCommander.start_turn_right(150)
                if CF.currentSequence_killingPill.is_set(): break
                time.sleep(0.8)
                # CF.motionCommander.back(1.5,1.5)
                # CF.motionCommander.start_turn_right(150)
                if CF.currentSequence_killingPill.is_set(): break
                time.sleep(0.8)
            print('fine quadrato di test')
            land_and_clear(CF)
        print('Drogno: %s. Inizio quadrato relativo di test' % CF.ID)
        threading.Thread(target=seq5, daemon=True).start()
#  non proprio una sequenza ma controllo manuale con gamepad:
def sequenzaSei(CF):
    def seq6():
        MAX_VELOCITY_XY   = 0.60
        MAX_VELOCITY_Z    = 0.95
        MAX_VELOCITY_YAW  = 120
        # import pygame
        import pygame
        # Initialize pygame for joystick support
        pygame.display.init()
        pygame.joystick.init()
        controller = pygame.joystick.Joystick(0)
        controller.init()
        comandi = {
            'destraSinistra':0,
            'avantiDietro': 0,
            'leftRight': 0,
            'changeHeight': 0
        }
        def getGamepadCommands():
            pygame.event.pump()

            for k in range(controller.get_numaxes()):
                if k == 2: 
                    # sys.stdout.write('%d:%+2.2f ' % (k, controller.get_axis(k)))
                    comandi['destraSinistra'] = controller.get_axis(k) * -1.
                elif k == 3:
                    comandi['avantiDietro'] = controller.get_axis(k) * -1.
                elif k == 1:
                    comandi['changeHeight'] = controller.get_axis(k)
                elif k == 0:
                    comandi['leftRight'] = controller.get_axis(k)
        
        CF.motionCommander.take_off(height=1.1,velocity=0.4)

        while not CF.currentSequence_killingPill.is_set():
            getGamepadCommands()
            
            if comandi['destraSinistra'] != 0:
                velocity_y = comandi['destraSinistra'] * MAX_VELOCITY_XY
            if comandi['avantiDietro'] != 0:
                velocity_x = comandi['avantiDietro'] * MAX_VELOCITY_XY
            if comandi['changeHeight'] != 0:
                velocity_z = comandi['changeHeight'] * MAX_VELOCITY_Z
            if comandi['leftRight'] != 0:
                velocity_yaw = comandi['leftRight'] * MAX_VELOCITY_YAW

            print ('moving with speed x:%s\ty:%s\tz:%s\tyaw:%s' % (velocity_x, velocity_y, velocity_z, velocity_z))
            CF.motionCommander.start_linear_motion( velocity_x, velocity_y, velocity_z, velocity_yaw)
            time.sleep(0.08)
        CF.motionCommander.land(0.3)
        
        CF.statoDiVolo = 'landing'
        CF.land()
        CF.statoDiVolo = 'idle'
        CF.currentSequence_killingPill.clear()
        print('fine quadratone di test')
    print('Drogno: %s. Inizio quadratone di test' % CF.ID)
    threading.Thread(target=seq6, daemon=True).start()

sequenze_test = [sequenzaUno, sequenzaDue, sequenzaTre, sequenzaQuattro, sequenzaCinque, sequenzaSei]
   




####################################################################     pre-recorded trajectories

def go_on_your_way(CF, sequenceNumber=0):
    if CF.isFlying:
        if GB.WE_ARE_FAKING_IT:
            CF.statoDiVolo = 'sequenza simulata!'
        else:
            trajectory_id = sequenceNumber
            CF.statoDiVolo = 'sequenza ' + str(sequenceNumber)
            # duration = CF.upload_trajectory(trajectory_id, figure8)
            # if sequenceNumber == 0:
            #     duration = CF.upload_trajectory(trajectory_id, CF.lastTrajectory)
            # else:
            #     duration = CF.upload_trajectory(trajectory_id, figure8)

            print ('eseguo la traiettoria %s lunga %s' % (sequenceNumber, CF.currentTrajectoryLenght))
            CF.run_trajectory(trajectory_id)
    else:
        print('not ready!')

def run_trajectory(CF, trajectory_id):
    commander = CF._cf.high_level_commander
    commander.takeoff(1.0, 2.0)
    time.sleep(3.0)
    relative = True
    commander.start_trajectory(trajectory_id, 1.0, relative)
    # commander.start_compressed
    time.sleep(CF.currentTrajectoryLenght)
    commander.land(0.0, 4.0)
    time.sleep(4)
    # commander.stop()
    pass
    #  un quadratone di 3mt x 3mt con high level commander
def upload_trajectory(CF, trajectory_id):
    trajectory_mem = CF._cf.mem.get_mems(MemoryElement.TYPE_TRAJ)[0]
    print ('sì! uppa la %s'% trajectory_id)
    total_duration = 0
    for row in CF.TRAJECTORIES[trajectory_id]:
        duration = row[0]
        x = Poly4D.Poly(row[1:9])
        y = Poly4D.Poly(row[9:17])
        z = Poly4D.Poly(row[17:25])
        yaw = Poly4D.Poly(row[25:33])
        trajectory_mem.poly4Ds.append(Poly4D(duration, x, y, z, yaw))
        total_duration += duration
    upload_result = Uploader().upload(trajectory_mem)
    if not upload_result:
        print('Upload failed, aborting!')
    CF._cf.high_level_commander.define_trajectory(trajectory_id, 0, len(trajectory_mem.poly4Ds))
    CF.currentTrajectoryLenght =  total_duration



# The trajectory to fly
# See https://github.com/whoenig/uav_trajectories for a tool to generate
# trajectories

# Duration,x^0,x^1,x^2,x^3,x^4,x^5,x^6,x^7,y^0,y^1,y^2,y^3,y^4,y^5,y^6,y^7,z^0,z^1,z^2,z^3,z^4,z^5,z^6,z^7,yaw^0,yaw^1,yaw^2,yaw^3,yaw^4,yaw^5,yaw^6,yaw^7
figure8 = [
    [1.050000, 0.000000, -0.000000, 0.000000, -0.000000, 0.830443, -0.276140, -0.384219, 0.180493, -0.000000, 0.000000, -0.000000, 0.000000, -1.356107, 0.688430, 0.587426, -0.329106, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.710000, 0.396058, 0.918033, 0.128965, -0.773546, 0.339704, 0.034310, -0.026417, -0.030049, -0.445604, -0.684403, 0.888433, 1.493630, -1.361618, -0.139316, 0.158875, 0.095799, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.620000, 0.922409, 0.405715, -0.582968, -0.092188, -0.114670, 0.101046, 0.075834, -0.037926, -0.291165, 0.967514, 0.421451, -1.086348, 0.545211, 0.030109, -0.050046, -0.068177, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.700000, 0.923174, -0.431533, -0.682975, 0.177173, 0.319468, -0.043852, -0.111269, 0.023166, 0.289869, 0.724722, -0.512011, -0.209623, -0.218710, 0.108797, 0.128756, -0.055461, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.560000, 0.405364, -0.834716, 0.158939, 0.288175, -0.373738, -0.054995, 0.036090, 0.078627, 0.450742, -0.385534, -0.954089, 0.128288, 0.442620, 0.055630, -0.060142, -0.076163, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.560000, 0.001062, -0.646270, -0.012560, -0.324065, 0.125327, 0.119738, 0.034567, -0.063130, 0.001593, -1.031457, 0.015159, 0.820816, -0.152665, -0.130729, -0.045679, 0.080444, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.700000, -0.402804, -0.820508, -0.132914, 0.236278, 0.235164, -0.053551, -0.088687, 0.031253, -0.449354, -0.411507, 0.902946, 0.185335, -0.239125, -0.041696, 0.016857, 0.016709, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.620000, -0.921641, -0.464596, 0.661875, 0.286582, -0.228921, -0.051987, 0.004669, 0.038463, -0.292459, 0.777682, 0.565788, -0.432472, -0.060568, -0.082048, -0.009439, 0.041158, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.710000, -0.923935, 0.447832, 0.627381, -0.259808, -0.042325, -0.032258, 0.001420, 0.005294, 0.288570, 0.873350, -0.515586, -0.730207, -0.026023, 0.288755, 0.215678, -0.148061, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [1.053185, -0.398611, 0.850510, -0.144007, -0.485368, -0.079781, 0.176330, 0.234482, -0.153567, 0.447039, -0.532729, -0.855023, 0.878509, 0.775168, -0.391051, -0.713519, 0.391628, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
]
figure8Triple = [
    [1.050000, 0.000000, -0.000000, 0.000000, -0.000000, 0.830443, -0.276140, -0.384219, 0.180493, -0.000000, 0.000000, -0.000000, 0.000000, -1.356107, 0.688430, 0.587426, -0.329106, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.710000, 0.396058, 0.918033, 0.128965, -0.773546, 0.339704, 0.034310, -0.026417, -0.030049, -0.445604, -0.684403, 0.888433, 1.493630, -1.361618, -0.139316, 0.158875, 0.095799, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.620000, 0.922409, 0.405715, -0.582968, -0.092188, -0.114670, 0.101046, 0.075834, -0.037926, -0.291165, 0.967514, 0.421451, -1.086348, 0.545211, 0.030109, -0.050046, -0.068177, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.700000, 0.923174, -0.431533, -0.682975, 0.177173, 0.319468, -0.043852, -0.111269, 0.023166, 0.289869, 0.724722, -0.512011, -0.209623, -0.218710, 0.108797, 0.128756, -0.055461, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.560000, 0.405364, -0.834716, 0.158939, 0.288175, -0.373738, -0.054995, 0.036090, 0.078627, 0.450742, -0.385534, -0.954089, 0.128288, 0.442620, 0.055630, -0.060142, -0.076163, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.560000, 0.001062, -0.646270, -0.012560, -0.324065, 0.125327, 0.119738, 0.034567, -0.063130, 0.001593, -1.031457, 0.015159, 0.820816, -0.152665, -0.130729, -0.045679, 0.080444, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.700000, -0.402804, -0.820508, -0.132914, 0.236278, 0.235164, -0.053551, -0.088687, 0.031253, -0.449354, -0.411507, 0.902946, 0.185335, -0.239125, -0.041696, 0.016857, 0.016709, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.620000, -0.921641, -0.464596, 0.661875, 0.286582, -0.228921, -0.051987, 0.004669, 0.038463, -0.292459, 0.777682, 0.565788, -0.432472, -0.060568, -0.082048, -0.009439, 0.041158, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.710000, -0.923935, 0.447832, 0.627381, -0.259808, -0.042325, -0.032258, 0.001420, 0.005294, 0.288570, 0.873350, -0.515586, -0.730207, -0.026023, 0.288755, 0.215678, -0.148061, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [1.053185, -0.398611, 0.850510, -0.144007, -0.485368, -0.079781, 0.176330, 0.234482, -0.153567, 0.447039, -0.532729, -0.855023, 0.878509, 0.775168, -0.391051, -0.713519, 0.391628, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [1.050000, 0.000000, -0.000000, 0.000000, -0.000000, 0.830443, -0.276140, -0.384219, 0.180493, -0.000000, 0.000000, -0.000000, 0.000000, -1.356107, 0.688430, 0.587426, -0.329106, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [1.053185, -0.398611, 0.850510, -0.144007, -0.485368, -0.079781, 0.176330, 0.234482, -0.153567, 0.447039, -0.532729, -0.855023, 0.878509, 0.775168, -0.391051, -0.713519, 0.391628, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.560000, 0.405364, -0.834716, 0.158939, 0.288175, -0.373738, -0.054995, 0.036090, 0.078627, 0.450742, -0.385534, -0.954089, 0.128288, 0.442620, 0.055630, -0.060142, -0.076163, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.560000, 0.001062, -0.646270, -0.012560, -0.324065, 0.125327, 0.119738, 0.034567, -0.063130, 0.001593, -1.031457, 0.015159, 0.820816, -0.152665, -0.130729, -0.045679, 0.080444, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.700000, -0.402804, -0.820508, -0.132914, 0.236278, 0.235164, -0.053551, -0.088687, 0.031253, -0.449354, -0.411507, 0.902946, 0.185335, -0.239125, -0.041696, 0.016857, 0.016709, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    ]

class Uploader:
    def __init__(self, CF):
        self._is_done = False
        self._sucess = True

    def upload(self, trajectory_mem):
        print('Uploading data')
        trajectory_mem.write_data(self._upload_done,
                                  write_failed_cb=self._upload_failed)

        while not self._is_done:
            time.sleep(0.2)

        return self._sucess

    def _upload_done(self, mem, addr):
        print('Data uploaded')
        self._is_done = True
        self._sucess = True

    def _upload_failed(self, mem, addr):
        print('Data upload failed')
        self._is_done = True
        self._sucess = False


def set_trajectory_path():
     # os.chdir(os.path.join('..', 'trajectoryRecorder', 'registrazioniOSC'))
    # patto = Path('./lastRecord.txt')
    # with open(patto, 'r') as f:
    #     lastRecordPath = f.read()
    #     print ('last record path: ' + lastRecordPath)
    pass
