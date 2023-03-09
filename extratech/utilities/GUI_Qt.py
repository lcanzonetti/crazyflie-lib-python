from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot as Slot
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QLineEdit, QTextEdit, QFormLayout
import sys, threading
from PIL import Image, ImageTk
import os, time, signal
from test_main import main
import GLOBALS as GB
import stenBaiatore, wakeUppatore
from common_utils import IDFromURI, exit_signal_handler, write
from test_utils import write_json

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

        self.widget = QWidget()
        self.grid = QGridLayout()
        self.onlyInt = QIntValidator()
        self.onlyInt.setRange(0, 99)

        #### Log

        self.textbox = QTextEdit(self,
            placeholderText = "Platform Testing Log",
            readOnly = True
        )
        self.textbox.setFont(QFont('Arial', 12))
        self.textbox.resize(400, 1200)
        self.text_function()

        #### Buttons

        ###### PROPELLER TESTING SECTION

        self.prop_label = QtWidgets.QLabel(self)
        self.prop_label.setText("Propeller Testing:")
        self.prop_label.setStyleSheet("border: 1px solid black;")

        ######## Propeller Test for Everyone
        self.prop_button = QtWidgets.QPushButton(self)
        self.prop_button.setText("Esegui Test Propellers per tutti")
        self.prop_button.clicked.connect(self.all_prop_test)

        ######## Type ID and proptest just one Drone
        self.prop_line = QtWidgets.QLineEdit(self)
        self.prop_line.setValidator(self.onlyInt)
        self.prop_line.returnPressed.connect(lambda: self.single_prop_test(int(self.prop_line.text())))

        self.proline_label = QtWidgets.QLabel(self)
        self.proline_label.setText("    Type Drone ID to test")

        ######## Take off and land
        self.takeoff_button = QtWidgets.QPushButton(self)
        self.takeoff_button.setText("Fai decollare i droni, poi atterrano")
        self.takeoff_button.clicked.connect(self.all_takeoff)

        ###### BATTERY TESTING SECTION

        self.batt_label = QtWidgets.QLabel(self)
        self.batt_label.setText("Battery Testing:")
        self.batt_label.setStyleSheet("border: 1px solid black;")

        ######## Battery Test for Everyone
        self.batt_button = QtWidgets.QPushButton(self)
        self.batt_button.setText("Esegui Test Batteria per tutti")
        self.batt_button.clicked.connect(self.all_batt_test)

        ######## Type ID and batttest just one Drone
        self.batt_line = QtWidgets.QLineEdit(self)
        self.batt_line.setValidator(self.onlyInt)
        self.batt_line.returnPressed.connect(lambda: self.single_batt_test(int(self.batt_line.text())))

        self.battline_label = QtWidgets.QLabel(self)
        self.battline_label.setText("    Type Drone ID to test")

        ###### RADIO TESTING SECTION
        self.radio_label = QtWidgets.QLabel(self)
        self.radio_label.setText("Radio Testing:")
        self.radio_label.setStyleSheet("border: 1px solid black;")

        ######## Radio test for Everyone
        self.radio_button = QtWidgets.QPushButton(self)
        self.radio_button.setText("Esegui Test Radio per tutti")
        self.radio_button.clicked.connect(self.all_radio_test)

        ######## Type ID and radiotest just one Drone
        self.radio_line = QtWidgets.QLineEdit(self)
        self.radio_line.setValidator(self.onlyInt)
        self.radio_line.returnPressed.connect(lambda: self.single_radio_test(int(self.radio_line.text())))

        self.radline_label = QtWidgets.QLabel(self)
        self.radline_label.setText("    Type Drone ID to test")

        #### CONNECTION SECTION 

        ###### Standby Everyone
        self.standby_button = QtWidgets.QPushButton(self)
        self.standby_button.setText("StenBaia tutti")
        self.standby_button.clicked.connect(self.standby_for_all)

        ###### Wakeup Everyone
        self.wakeup_button = QtWidgets.QPushButton(self)
        self.wakeup_button.setText("WakeUppa tutti")
        self.wakeup_button.clicked.connect(self.wake_up_all)

        #### LOG MANIPULATION

        ###### Clear Log
        self.clearlog_button = QtWidgets.QPushButton(self)
        self.clearlog_button.setText("Pulisci Log")
        self.clearlog_button.clicked.connect(self.clear_log)

        ###### Write json with results
        self.writejson_button = QtWidgets.QPushButton(self)
        self.writejson_button.setText("Scrivi Json con Risultati")
        self.writejson_button.clicked.connect(self.scrivi_json)

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
        self.grid.addWidget(self.standby_button, 12, 0, 1, 4)
        self.grid.addWidget(self.wakeup_button, 13, 0, 1, 4)
        self.grid.addWidget(self.takeoff_button, 14, 0, 1, 4)
        self.grid.addWidget(self.clearlog_button, 18, 6, 1, 1)
        self.grid.addWidget(self.textbox, 0, 5, 16, 1)
        self.grid.addWidget(self.writejson_button, 17, 6, 1, 1)

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

    def wake_up_all(self):
        self.worker_thread = QThread()
        self.worker = Worker()

        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

        ###### Disable Buttons while connecting
        
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

    def standby_for_all(self):
        for uro in GB.available:
            id = IDFromURI(uro)
            GB.data_d[id].close_link()
            stenBaiatore.standBySingle(uro)
    
    def clear_log(self):
        self.textbox.clear()
        clear_text = open(os.path.join(__location__, "log.txt"), mode = "w")
        clear_text.close()

    def all_takeoff(self):
        for uro in GB.available:
            id = IDFromURI(uro)
            GB.data_d[id].test_manager.decollo_atterraggio()
    
    def scrivi_json(self):
        write_json(__location__)

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

#### Window initialization

def window():
    app = QApplication(sys.argv)
    win = MyWindow()

    signal.signal(signal.SIGINT, exit_signal_handler)

    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    window()
    
