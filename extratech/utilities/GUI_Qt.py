from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QDir, pyqtSlot as Slot
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QLineEdit, QTextEdit, QFormLayout, QFileDialog, QToolTip
import sys, threading
import numpy as np
from PIL import Image, ImageTk
import os, time, signal, math
from test_main import main
import GLOBALS as GB
import stenBaiatore, wakeUppatore
from common_utils import IDFromURI, exit_signal_handler, write
from test_utils import write_json
from flash_util import flasha_firmware_subprocess

#### VARIABLES
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


file_to_delete = open(os.path.join(__location__, "log.txt"), mode = "w")
file_to_delete.close()

dir_exists = os.path.exists(__location__ + './Test_Resultsss')

if not dir_exists: os.makedirs(__location__ + './Test_Resultsss')

# isExist    = os.path.exists(proj_path[0] + '/Test_Resultsss')                  ### Chekka se esiste cartella dove scrivere json dei risultati, se no la crea
# if not isExist: os.makedirs(proj_path[0] + '/Test_Resultsss')

class MyWindow(QMainWindow):
    text_requested = Signal(str)

    def __init__(self):
        super(MyWindow, self).__init__()
        # self.setGeometry(200, 200, 300, 300)
        self.setWindowTitle("Extratech Testing Platform")
        self.initUI()
    
    def initUI(self):

        QToolTip.setFont(QFont('Arial', 10))

        self.widget = QWidget()
        self.grid = QGridLayout()
        self.onlyInt = QIntValidator()
        self.onlyInt.setRange(0, 99)
        self.powerMax = QIntValidator()
        self.powerMax.setRange(0, 65534)
       
        #### Log

        self.textbox = QTextEdit(self,
            placeholderText = "Platform Testing Log",
            readOnly = True
        )
        self.textbox.setFont(QFont('Arial', 12))
        self.textbox.resize(400, 1200)
        self.text_function()
        # self.giveme_battery()

        #### Buttons

        ###### HOW MANY DRONES SECTION

        self.howmany_label = QtWidgets.QLabel(self)
        self.howmany_label.setText("How many Drognos we have?")
        self.howmany_label.setStyleSheet("border: 1px solid black;")

        ######## Scrivi quanti droni abbiamo

        self.howmany_line = QtWidgets.QLineEdit(self)
        self.howmany_line.setValidator(self.onlyInt)
        self.howmany_line.returnPressed.connect(lambda: self.set_howmany(int(self.howmany_line.text())))
        self.howmany_line.setToolTip("Set the number of drognos you have in the swarm, default 9.\nNote that if you have non-sequential IDs for you Drones, this number should be equal to the highest ID you have.")

        ###### PROPELLER TESTING SECTION

        self.prop_label = QtWidgets.QLabel(self)
        self.prop_label.setText("Propeller Testing:")
        self.prop_label.setStyleSheet("border: 1px solid black;")

        ######## Propeller Test for Everyone
        self.prop_button = QtWidgets.QPushButton(self)
        self.prop_button.setText("Propellers Test for Everyone")
        self.prop_button.clicked.connect(self.all_prop_test)
        self.prop_button.setToolTip("Execute Propeller Test for each and every succesfully connected drone in the swarm.")

        ######## Testa solo un motore

        ## Power select
        self.power_line = QtWidgets.QLineEdit(self)
        self.power_line.setValidator(self.powerMax)
        self.power_line.returnPressed.connect(lambda: self.change_power(int(self.power_line.text())))
        self.power_line.setToolTip("Set power to thest the motor at. Range is from 0 to 65534. (CAREFUL!!!)")

        self.powerline_label = QtWidgets.QLabel(self)
        self.powerline_label.setText("    Type motor power to test")
        
        ## M1
        self.motore1_button = QtWidgets.QPushButton(self)
        self.motore1_button.setText("Test Motor 1")
        self.motore1_button.clicked.connect(lambda: self.testa_un_motore(1))

        ## M21
        self.motore2_button = QtWidgets.QPushButton(self)
        self.motore2_button.setText("Test Motor 2")
        self.motore2_button.clicked.connect(lambda: self.testa_un_motore(2))

        ## M3
        self.motore3_button = QtWidgets.QPushButton(self)
        self.motore3_button.setText("Test Motor 3")
        self.motore3_button.clicked.connect(lambda: self.testa_un_motore(3))

        ## M4
        self.motore4_button = QtWidgets.QPushButton(self)
        self.motore4_button.setText("Test Motor 4")
        self.motore4_button.clicked.connect(lambda: self.testa_un_motore(4))

        ######## Type ID and proptest just one Drone
        self.prop_line = QtWidgets.QLineEdit(self)
        self.prop_line.setValidator(self.onlyInt)
        self.prop_line.returnPressed.connect(lambda: self.single_prop_test(int(self.prop_line.text())))
        self.prop_line.setToolTip("Type single Drone ID to execute Propeller Test for.")

        self.proline_label = QtWidgets.QLabel(self)
        self.proline_label.setText("    Type Drone ID to test")

        ###### BATTERY TESTING SECTION

        self.batt_label = QtWidgets.QLabel(self)
        self.batt_label.setText("Battery Testing:")
        self.batt_label.setStyleSheet("border: 1px solid black;")

        ######## Battery Test for Everyone
        self.batt_button = QtWidgets.QPushButton(self)
        self.batt_button.setText("Battery Test for Everyone")
        self.batt_button.clicked.connect(self.all_batt_test)
        self.batt_button.setToolTip("Execute Battery Test for each and every succesfully connected drone in the swarm.")

        ######## Type ID and batttest just one Drone
        self.batt_line = QtWidgets.QLineEdit(self)
        self.batt_line.setValidator(self.onlyInt)
        self.batt_line.returnPressed.connect(lambda: self.single_batt_test(int(self.batt_line.text())))
        self.batt_line.setToolTip("Type single Drone ID to execute Battery Test for.")

        self.battline_label = QtWidgets.QLabel(self)
        self.battline_label.setText("    Type Drone ID to test")

        ######## Ask battery voltage
        self.askbatt_button = QtWidgets.QPushButton(self)
        self.askbatt_button.setText("Ask battery for drones... ")
        self.askbatt_button.clicked.connect(self.want_to_know_the_battery)
        self.askbatt_button.setToolTip("Ask battery status for each and every succesfully connected drone in the swarm.")

        ###### RADIO TESTING SECTION
        self.radio_label = QtWidgets.QLabel(self)
        self.radio_label.setText("Radio Testing:")
        self.radio_label.setStyleSheet("border: 1px solid black;")

        ######## Radio test for Everyone
        self.radio_button = QtWidgets.QPushButton(self)
        self.radio_button.setText("Radio Test for Everyone")
        self.radio_button.clicked.connect(self.all_radio_test)
        self.radio_button.setToolTip("Execute Radio Test for each and every succesfully connected dron in the swarm.")

        ######## Type ID and radiotest just one Drone
        self.radio_line = QtWidgets.QLineEdit(self)
        self.radio_line.setValidator(self.onlyInt)
        self.radio_line.returnPressed.connect(lambda: self.single_radio_test(int(self.radio_line.text())))
        self.radio_line.setToolTip("Type single Drone ID to execute Radio Test for.")

        self.radline_label = QtWidgets.QLabel(self)
        self.radline_label.setText("    Type Drone ID to test")

        #### LED SECTION
        self.led_label = QtWidgets.QLabel(self)
        self.led_label.setText("Led Testing:")
        self.led_label.setStyleSheet("border: 1px solid black;")

        ###### Led Test for everyone
        self.all_led_button = QtWidgets.QPushButton(self)
        self.all_led_button.setText("LED Test for Everyone")
        self.all_led_button.clicked.connect(self.all_ledtest)
        self.all_led_button.setToolTip("Execute LED Test for each and every succesfully connected drone in the swarm.")

        #### STABILITY SECTION

        self.takeoff_label = QtWidgets.QLabel(self)
        self.takeoff_label.setText("Stability Section:")
        self.takeoff_label.setStyleSheet("border: 1px solid black;")

        ###### Take off and land

        self.takeoff_button = QtWidgets.QPushButton(self)
        self.takeoff_button.setText("Drognos Take off, then land")
        self.takeoff_button.clicked.connect(self.all_takeoff)
        self.takeoff_button.setToolTip("When clicked, all drones in the swarm will take off, hover for some seconds, then land.")

        #### CONNECTION SECTION

        self.connection_label = QtWidgets.QLabel(self)
        self.connection_label.setText("Connection Section:")
        self.connection_label.setStyleSheet("border: 1px solid black;")

        ###### Standby Everyone
        self.standby_button = QtWidgets.QPushButton(self)
        self.standby_button.setText("Standby Everyone")
        self.standby_button.clicked.connect(self.standby_for_all)
        self.standby_button.setToolTip("When clicked, Standby all succesfully connected drones in the swarm.")

        ###### Wakeup Everyone
        self.wakeup_button = QtWidgets.QPushButton(self)
        self.wakeup_button.setText("Wakeup Everyone")
        self.wakeup_button.clicked.connect(self.wake_up_all)
        self.wakeup_button.setToolTip("When clicked, tries to wakeup and connect to each Drone whose ID goes from '...00' to the number of drones you set.")

        #### LOG MANIPULATION

        ###### Clear Log
        self.clearlog_button = QtWidgets.QPushButton(self)
        self.clearlog_button.setText("Clear Log")
        self.clearlog_button.clicked.connect(self.clear_log)
        self.clearlog_button.setToolTip("Clear the Log.")

        ###### Write json with results
        self.writejson_button = QtWidgets.QPushButton(self)
        self.writejson_button.setText("Write Results Json")
        self.writejson_button.clicked.connect(self.scrivi_json)
        self.writejson_button.setToolTip("Create a Json file which includes all the test results for all the drones in the swarm.")

        #### FLASH

        self.flash_label = QtWidgets.QLabel(self)
        self.flash_label.setText("Flashing Section:")
        self.flash_label.setStyleSheet("border: 1px solid black;")

        ###### Prepare Drogni to Flash

        self.prepare_button = QtWidgets.QPushButton(self)
        self.prepare_button.setText("1: Prepare Drognos for Flashing... ")
        self.prepare_button.clicked.connect(self.prepare_for_flashing)
        self.prepare_button.setToolTip("Standby all drones in the swarm, then Wakes up everyone without connecting.")

        ###### Browse File to Flash

        self.trovafile_button = QtWidgets.QPushButton(self)
        self.trovafile_button.setText("2: Browse for firmware... ")
        self.trovafile_button.clicked.connect(self.browse_for_firmware)
        self.trovafile_button.setToolTip("Browse for firmware file (.zip or otherwise)")

        ###### Flasha tutti i drogni trovati
        
        self.flashatutti_button = QtWidgets.QPushButton(self)
        self.flashatutti_button.setText("3: Flash all Drognos we have... ")
        self.flashatutti_button.clicked.connect(self.flash_all_crazyflies)
        self.flashatutti_button.setToolTip("Flash all drones succesfully woke upped by preparation sequence.")

        ###### Select drogno to Flash
        self.flash_line = QtWidgets.QLineEdit(self)
        self.flash_line.setPlaceholderText("Write precise addresses")
        self.flash_line.setValidator(self.onlyInt)
        self.flash_line.returnPressed.connect(lambda: self.flash_crazyflie(self.flash_line.text()))
        self.flash_line.setToolTip("You have to write the 'exact' drone ID for this to work. For example Drone ID '1' should be written as '01' and so on.")

        self.flashline_label = QtWidgets.QLabel(self)
        self.flashline_label.setText("    Type Drone ID to Flash")

        
        #### Add Widgets to grid
        self.grid.addWidget(self.prop_label, 0, 0, 1, 4)
        self.grid.addWidget(self.prop_button, 1, 0, 1, 4)
        self.grid.addWidget(self.proline_label, 2, 0, 1, 4)
        self.grid.addWidget(self.prop_line, 3, 0, 1, 4)
        self.grid.addWidget(self.batt_label, 4, 0, 1, 4)
        self.grid.addWidget(self.batt_button, 5, 0, 1, 4)
        self.grid.addWidget(self.battline_label, 6, 0, 1, 4)
        self.grid.addWidget(self.batt_line, 7, 0, 1, 4)
        self.grid.addWidget(self.radio_label, 8, 0, 1, 4)
        self.grid.addWidget(self.radio_button, 9, 0, 1, 4)
        self.grid.addWidget(self.radline_label, 10, 0, 1, 4)
        self.grid.addWidget(self.radio_line, 11, 0, 1, 4)
        self.grid.addWidget(self.led_label, 12, 0, 1, 4)
        self.grid.addWidget(self.all_led_button, 13, 0, 1, 4)
        self.grid.addWidget(self.takeoff_label, 14, 0, 1, 4)
        self.grid.addWidget(self.takeoff_button, 15, 0, 1, 4)
        self.grid.addWidget(self.connection_label, 16, 0, 1, 4)
        self.grid.addWidget(self.standby_button, 17, 0, 1, 4)
        self.grid.addWidget(self.wakeup_button, 18, 0, 1, 4)
        self.grid.addWidget(self.flash_label, 2, 16, 1, 2)
        self.grid.addWidget(self.flashline_label, 6, 16, 1, 2)
        self.grid.addWidget(self.flash_line, 7, 16, 1, 2)
        self.grid.addWidget(self.prepare_button, 3, 16, 1, 2)
        self.grid.addWidget(self.trovafile_button, 4, 16, 1, 2)
        self.grid.addWidget(self.flashatutti_button, 5, 16, 1, 2)
        self.grid.addWidget(self.howmany_label, 0, 16, 1, 2)
        self.grid.addWidget(self.howmany_line, 1, 16, 1, 2)
        self.grid.addWidget(self.clearlog_button, 20, 16, 1, 2)
        self.grid.addWidget(self.askbatt_button, 21, 16, 1, 2)
        self.grid.addWidget(self.textbox, 0, 5, 19, 10)
        self.grid.addWidget(self.writejson_button, 19, 16, 1, 2)
        self.grid.addWidget(self.powerline_label, 20, 0, 1, 4)
        self.grid.addWidget(self.power_line, 21, 0, 1, 4)
        self.grid.addWidget(self.motore1_button, 22, 0, 1, 1)
        self.grid.addWidget(self.motore2_button, 22, 1, 1, 1)
        self.grid.addWidget(self.motore3_button, 23, 0, 1, 1)
        self.grid.addWidget(self.motore4_button, 23, 1, 1, 1)

        self.widget.setLayout(self.grid)
        self.setCentralWidget(self.widget)
            

    #### Write log to TextBox
    
    def update_text(self, t):
        self.textbox.clear()
        self.textbox.append(t)

    #### Main?

    def text_function(self):
        self.text_thread = QThread()

        self.reader = Reader()

        self.reader.moveToThread(self.text_thread)

        self.reader.testo.connect(self.update_text)
        self.text_requested.connect(self.reader.leggi)

        self.text_thread.started.connect(self.reader.leggi)

        self.text_thread.start()

    #### FUNCTIONS
    
    def create_button(self):
        chunk_size = 5
        GB.termination_flag = False
        if len(GB.button_array) != 0:
            for i in range(len(GB.button_array)):
                self.grid.removeWidget(GB.button_array[i])    
        GB.button_array = []
        for i in range(len(GB.available)):
            GB.button_array.append(QtWidgets.QProgressBar())
            GB.button_array[i].setTextVisible(True)
            GB.button_array[i].setMinimum(0)
            GB.button_array[i].setMaximum(10)
            GB.button_array[i].setFormat('%v%')
        for j in range(int(math.ceil(len(GB.button_array)/chunk_size))):
            if (len(GB.button_array)%chunk_size) != 0:
                if j == (int(math.ceil(len(GB.button_array)/chunk_size)) - 1):
                    for k in range(len(GB.button_array)%chunk_size):
                        self.grid.addWidget(GB.button_array[k+(j*chunk_size)], 20+j, 5+k, 1, 1)
                else:
                    for k in range(chunk_size):
                        self.grid.addWidget(GB.button_array[k+(j*chunk_size)], 20+j, 5+k, 1, 1)
        self.want_to_know_the_battery()

    ###### How many drones in the swarm? (default 9)
    def set_howmany(self, quanti):
        GB.numero_droni = quanti
        write(GB.numero_droni)

    ###### Propeller test functions
    def all_prop_test(self):
        try:
            for uro in GB.available:
                id = IDFromURI(uro)
                GB.data_d[id].test_manager.single_drone_prop_test()
        except KeyError:
            write("No Drones connected!")

    def single_prop_test(self, id):
        try:        
            GB.data_d[id].test_manager.single_drone_prop_test()
        except KeyError:
            write("Drone ID not in swarm!")

    ###### Battery test functions
    def all_batt_test(self):
        try:
            for uro in GB.available:
                id = IDFromURI(uro)
                GB.data_d[id].test_manager.single_drone_batt_test()
        except KeyError:
            write("No Drones connected!")
    
    def single_batt_test(self, id):
        try:
            GB.data_d[id].test_manager.single_drone_batt_test()
        except KeyError:
            write("Drone ID not in swarm!")

    ###### Radio test functions
    def all_radio_test(self):
        self.allradio_thread = QThread()
        self.allradio = AllRadio()

        self.allradio.moveToThread(self.allradio_thread)

        self.allradio_thread.started.connect(self.allradio.all_the_radio)
        self.allradio.finished.connect(self.allradio_thread.quit)
        self.allradio.finished.connect(self.allradio.deleteLater)
        self.allradio_thread.finished.connect(self.allradio_thread.deleteLater)

        self.allradio_thread.start()

    def single_radio_test(self, id):
        global id_totest

        id_totest = id

        self.oneradio_thread = QThread()
        self.oneradio = SingleRadio()

        self.oneradio.moveToThread(self.oneradio_thread)
        
        self.oneradio_thread.started.connect(self.oneradio.justone_radio)
        self.oneradio.finished.connect(self.oneradio_thread.quit)
        self.oneradio.finished.connect(self.oneradio.deleteLater)
        self.oneradio_thread.finished.connect(self.oneradio_thread.deleteLater)

        self.oneradio_thread.start()

    ###### Motor test functions
    def change_power(self, power):
        GB.power = power

    def testa_un_motore(self, motore):

        GB.qualemotore = motore

        self.single_motor_thread = QThread(parent=self)
        self.single_motor = singleMotor()

        self.single_motor.moveToThread(self.single_motor_thread)

        self.single_motor_thread.started.connect(self.single_motor.justonemotor)
        self.single_motor.finished.connect(self.single_motor_thread.quit)
        self.single_motor.finished.connect(self.single_motor.deleteLater)
        self.single_motor_thread.finished.connect(self.single_motor_thread.deleteLater)
        
        self.single_motor_thread.start()

    ###### Wakeup/Standby functions
    def wake_up_all(self):

        self.worker_thread = QThread()
        self.worker = Worker()
        GB.termination_flag = True

        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()
        
        self.worker_thread.finished.connect(self.create_button)
        # self.worker_thread.finished.connect(self.want_to_know_the_battery)

        #### DISABLE ALL BUTTONS WHILE DOING STUFF

        self.prop_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.prop_button.setEnabled(True))
        self.standby_button.setEnabled(False)
        self.batt_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.batt_button.setEnabled(True))
        self.batt_line.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.batt_line.setEnabled(True))
        self.worker_thread.finished.connect(lambda: self.standby_button.setEnabled(True))
        self.prop_line.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.prop_line.setEnabled(True))
        self.wakeup_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.wakeup_button.setEnabled(True))
        self.radio_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.radio_button.setEnabled(True))
        self.radio_line.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.radio_line.setEnabled(True))  
        self.takeoff_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.takeoff_button.setEnabled(True))
        self.motore1_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.motore1_button.setEnabled(True))
        self.motore2_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.motore2_button.setEnabled(True))
        self.motore3_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.motore3_button.setEnabled(True))
        self.motore4_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.motore4_button.setEnabled(True))
        self.power_line.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.power_line.setEnabled(True))
        self.all_led_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.all_led_button.setEnabled(True))
        self.prepare_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.prepare_button.setEnabled(True))
        self.trovafile_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.trovafile_button.setEnabled(True))
        self.flashatutti_button.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.flashatutti_button.setEnabled(True))
        self.flash_line.setEnabled(False)
        self.worker_thread.finished.connect(lambda: self.flash_line.setEnabled(True))

    def standby_for_all(self):
        for uro in GB.available:
            id = IDFromURI(uro)
            try:
                GB.data_d[id].close_link()
                stenBaiatore.standBySingle(uro)
            except KeyError as e:
                write("Non puoi Stenbaiare se prima non ti connetti per bene!")

    def all_takeoff(self):
        self.alltakeoff_thread = QThread()
        self.alltakeoff = TakeOFF()

        self.alltakeoff.moveToThread(self.alltakeoff_thread)

        self.alltakeoff_thread.started.connect(self.alltakeoff.takeoff_all)
        self.alltakeoff.finished.connect(self.alltakeoff_thread.quit)
        self.alltakeoff.finished.connect(self.alltakeoff.deleteLater)
        self.alltakeoff_thread.finished.connect(self.alltakeoff_thread.deleteLater)

        self.alltakeoff_thread.start()

        # for uro in GB.available:
        #     id = IDFromURI(uro)
        #     GB.data_d[id].test_manager.decollo_atterraggio()
    
    def all_ledtest(self):
        self.allledtest_thread = QThread()
        self.allledtest = ledTest()

        self.allledtest.moveToThread(self.allledtest_thread)

        self.allledtest_thread.started.connect(self.allledtest.ledtest_all)
        self.allledtest.finished.connect(self.allledtest_thread.quit)
        self.allledtest.finished.connect(self.allledtest.deleteLater)
        self.allledtest_thread.finished.connect(self.allledtest_thread.deleteLater)

        self.allledtest_thread.start()
    
    ###### Flashing functions
    def prepare_for_flashing(self):
        self.prepare_thread = QThread()
        self.prepare = prepareFlashing()

        self.prepare.moveToThread(self.prepare_thread)
        
        self.prepare_thread.started.connect(self.prepare.prepariamo_drogni)
        self.prepare.finished.connect(self.prepare_thread.quit)
        self.prepare.finished.connect(self.prepare.deleteLater)
        self.prepare_thread.finished.connect(self.prepare_thread.deleteLater)

        self.prepare_thread.start()

        #### DISABLE ALL BUTTONS WHILE DOING STUFF

        self.prop_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.prop_button.setEnabled(True))
        self.standby_button.setEnabled(False)
        self.batt_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.batt_button.setEnabled(True))
        self.batt_line.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.batt_line.setEnabled(True))
        self.prepare_thread.finished.connect(lambda: self.standby_button.setEnabled(True))
        self.prop_line.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.prop_line.setEnabled(True))
        self.wakeup_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.wakeup_button.setEnabled(True))
        self.radio_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.radio_button.setEnabled(True))
        self.radio_line.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.radio_line.setEnabled(True))  
        self.takeoff_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.takeoff_button.setEnabled(True))
        self.motore1_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.motore1_button.setEnabled(True))
        self.motore2_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.motore2_button.setEnabled(True))
        self.motore3_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.motore3_button.setEnabled(True))
        self.motore4_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.motore4_button.setEnabled(True))
        self.power_line.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.power_line.setEnabled(True))
        self.all_led_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.all_led_button.setEnabled(True))
        self.prepare_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.prepare_button.setEnabled(True))
        self.trovafile_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.trovafile_button.setEnabled(True))
        self.flashatutti_button.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.flashatutti_button.setEnabled(True))
        self.flash_line.setEnabled(False)
        self.prepare_thread.finished.connect(lambda: self.flash_line.setEnabled(True))

    def browse_for_firmware(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self)
        GB.FILE_TO_FLASH = filename
        write("Selected file at %s" % filename)
    
    def flash_crazyflie(self, drogno):
        global drogno_to_flash

        drogno_to_flash = drogno

        self.flashing_drogno_thread = QThread()
        self.flashing_drogno = flashDrogno()

        self.flashing_drogno.moveToThread(self.flashing_drogno_thread)

        self.flashing_drogno_thread.started.connect(self.flashing_drogno.flash_drogno)
        self.flashing_drogno.finished.connect(self.flashing_drogno_thread.quit)
        self.flashing_drogno.finished.connect(self.flashing_drogno.deleteLater)
        self.flashing_drogno_thread.finished.connect(self.flashing_drogno_thread.deleteLater)

        self.flashing_drogno_thread.start()

        #### DISABLE ALL BUTTONS WHILE DOING STUFF

        self.prop_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.prop_button.setEnabled(True))
        self.standby_button.setEnabled(False)
        self.batt_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.batt_button.setEnabled(True))
        self.batt_line.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.batt_line.setEnabled(True))
        self.flashing_drogno_thread.finished.connect(lambda: self.standby_button.setEnabled(True))
        self.prop_line.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.prop_line.setEnabled(True))
        self.wakeup_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.wakeup_button.setEnabled(True))
        self.radio_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.radio_button.setEnabled(True))
        self.radio_line.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.radio_line.setEnabled(True))  
        self.takeoff_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.takeoff_button.setEnabled(True))
        self.motore1_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.motore1_button.setEnabled(True))
        self.motore2_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.motore2_button.setEnabled(True))
        self.motore3_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.motore3_button.setEnabled(True))
        self.motore4_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.motore4_button.setEnabled(True))
        self.power_line.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.power_line.setEnabled(True))
        self.all_led_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.all_led_button.setEnabled(True))
        self.prepare_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.prepare_button.setEnabled(True))
        self.trovafile_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.trovafile_button.setEnabled(True))
        self.flashatutti_button.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.flashatutti_button.setEnabled(True))
        self.flash_line.setEnabled(False)
        self.flashing_drogno_thread.finished.connect(lambda: self.flash_line.setEnabled(True))
    
    def flash_all_crazyflies(self):
        self.flashing_alldrogni_thread = QThread()
        self.flashing_alldrogni = flashTuttiDrogni()

        self.flashing_alldrogni.moveToThread(self.flashing_alldrogni_thread)

        self.flashing_alldrogni_thread.started.connect(self.flashing_alldrogni.flash_tutti_drogni)
        self.flashing_alldrogni.finished.connect(self.flashing_alldrogni_thread.quit)
        self.flashing_alldrogni.finished.connect(self.flashing_alldrogni.deleteLater)
        self.flashing_alldrogni_thread.finished.connect(self.flashing_alldrogni_thread.deleteLater)

        self.flashing_alldrogni_thread.start()

        #### DISABLE ALL BUTTONS WHILE DOING STUFF

        self.prop_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.prop_button.setEnabled(True))
        self.standby_button.setEnabled(False)
        self.batt_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.batt_button.setEnabled(True))
        self.batt_line.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.batt_line.setEnabled(True))
        self.flashing_alldrogni_thread.finished.connect(lambda: self.standby_button.setEnabled(True))
        self.prop_line.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.prop_line.setEnabled(True))
        self.wakeup_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.wakeup_button.setEnabled(True))
        self.radio_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.radio_button.setEnabled(True))
        self.radio_line.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.radio_line.setEnabled(True))  
        self.takeoff_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.takeoff_button.setEnabled(True))
        self.motore1_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.motore1_button.setEnabled(True))
        self.motore2_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.motore2_button.setEnabled(True))
        self.motore3_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.motore3_button.setEnabled(True))
        self.motore4_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.motore4_button.setEnabled(True))
        self.power_line.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.power_line.setEnabled(True))
        self.all_led_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.all_led_button.setEnabled(True))
        self.prepare_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.prepare_button.setEnabled(True))
        self.trovafile_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.trovafile_button.setEnabled(True))
        self.flashatutti_button.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.flashatutti_button.setEnabled(True))
        self.flash_line.setEnabled(False)
        self.flashing_alldrogni_thread.finished.connect(lambda: self.flash_line.setEnabled(True))

    ###### Json and textbox functions
    def scrivi_json(self):
        write_json(__location__)       

    def clear_log(self):
        self.textbox.clear()
        clear_text = open(os.path.join(__location__, "log.txt"), mode = "w")
        clear_text.close()

    def want_to_know_the_battery(self):
        self.check_battery_thread = QThread()
        self.check_battery = BatteryCheck()

        self.check_battery.moveToThread(self.check_battery_thread)
        self.check_battery_thread.started.connect(self.check_battery.check_the_battery)
        self.check_battery.finished.connect(self.check_battery_thread.quit)
        self.check_battery.finished.connect(self.check_battery.deleteLater)
        self.check_battery.data.connect(self.reportVoltage)

        self.check_battery_thread.start()

    def reportVoltage(self, data):
        try:
            GB.button_array[data[1]].setFormat("Drone %s: %s" % (IDFromURI(GB.available[data[1]]), round(data[0], 2)))
            GB.button_array[data[1]].setAlignment(QtCore.Qt.AlignCenter)
            GB.button_array[data[1]].setValue(round(data[0], 2))
        except IndexError:
            pass



#### Test Main Worker

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        main()
        self.finished.emit()

#### Logger Worker

class Reader(QObject):
    testo = Signal(str)

    def leggi(self):
        self.devolegge = True
        current_text = ""
        prec_text = ""

        while True:
            current_text = ''.join(open(os.path.join(__location__, "log.txt")))

            if current_text != prec_text:
                self.testo.emit(current_text)
                prec_text = current_text
            else:
                pass
            time.sleep(0.1)

class BatteryCheck(QObject):
    finished = pyqtSignal()
    voltage = pyqtSignal(float)
    index = pyqtSignal(int)
    data = pyqtSignal(list)

    def check_the_battery(self):
        bar_index = 0
        while not GB.termination_flag:
            for uro in GB.available:
                if bar_index == len(GB.available): bar_index = 0
                id = IDFromURI(uro)
                v = GB.data_d[id].test_manager.get_battery_voltage()
                self.voltage.emit(v)
                self.index.emit(bar_index)
                self.data.emit([v, bar_index])
                bar_index += 1
            time.sleep(1)
        
        self.finished.emit()


#### Radio Workers

class AllRadio(QObject):
    finished = pyqtSignal()

    def all_the_radio(self):
        for uro in GB.available:
            id = IDFromURI(uro)
            GB.data_d[id].test_manager.single_drone_radio_test()
        self.finished.emit()

class SingleRadio(QObject):
    finished = pyqtSignal()

    def justone_radio(self):
        try:
            GB.data_d[id_totest].test_manager.single_drone_radio_test()
        except KeyError:
            write("Drone ID not in swarm!")
        self.finished.emit()

#### TAKEOFF Workers

class TakeOFF(QObject):
    finished = pyqtSignal()

    def takeoff_all(self):
        for uro in GB.available:
            id = IDFromURI(uro)
            GB.data_d[id].test_manager.decollo_atterraggio()
            
        self.finished.emit()

#### LED Workers

class ledTest(QObject):
    finished = pyqtSignal()

    def ledtest_all(self):
        for uro in GB.available:
            try:
                id = IDFromURI(uro)
                GB.data_d[id].test_manager.led_test()
            except KeyError:
                write("Led Test did not go well for drone %s" % id)
        self.finished.emit()

#### MOTOR Workers

class singleMotor(QObject):
    finished = pyqtSignal()

    def justonemotor(self):
        for uro in GB.available:
            try:
                id = IDFromURI(uro)
                GB.data_d[id].test_manager.single_motor_test()
            except KeyError:
                write("Single Motor Test did not go well for drone %s" % id)
        self.finished.emit()

#### FLASH Workers

class prepareFlashing(QObject):
    finished = pyqtSignal()

    def prepariamo_drogni(self):
        for uro in GB.available:
            id = IDFromURI(uro)
            GB.data_d[id].close_link()
            stenBaiatore.standBySingle(uro)
        
        wakeUppatore.wekappa(GB.numero_droni)

        self.finished.emit()

class flashDrogno(QObject):
    finished = pyqtSignal()
    
    def flash_drogno(self):
        for drogno in GB.available:
            s = drogno
            f1 = s[len(s) - 1]
            f2 = s[len(s) - 2] 
            if drogno_to_flash == f2 + f1:
                write('Flashing firmware to drone %s ' % drogno)
                flasha_firmware_subprocess(drogno)

        self.finished.emit()

class flashTuttiDrogni(QObject):
    finished = pyqtSignal()
    
    def flash_tutti_drogni(self):
        for drogno in GB.available:
            write('Flashing firmware to drone %s ' % drogno)
            flasha_firmware_subprocess(drogno)

        self.finished.emit()

#### Window initialization

def window():
    app = QApplication(sys.argv)
    win = MyWindow()

    signal.signal(signal.SIGINT, exit_signal_handler)

    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    window()
    
