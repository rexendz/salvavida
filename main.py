from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from HCSerial import SerialListener
import RPi.GPIO as GPIO
import os
import sys
import time
from firebase_admin import credentials
from firebase_admin import db
import firebase_admin

userpath = os.getenv("HOME")
print(userpath)
cred = credentials.Certificate(userpath + '/salvavida/firebase.json')
firebase_admin.initialize_app(cred, {
'databaseURL' : 'https://salvavida-e0f92-default-rtdb.firebaseio.com/'
})
root = db.reference()




class Window(QWidget): # Inherits from QWidget class
    def __init__(self):
        super().__init__() # Initializes the QWidget class
        self.title = "SALVA VIDA" # Title Name
        self.left = 0 # Window Coordinates
        self.top = 0  # Window Coordinates
        self.width = 480 # Window Width
        self.height = 320 # Window Height
        self.userpath = os.getenv("HOME") # Get user path directory
        self.vbox = QVBoxLayout() # Vertical Layout
        self.gbox = QGridLayout() # Gridbox Layout

    def InitWindow(self):
        self.setWindowTitle(self.title) # Sets the window title to the title name declared earlier
        self.setGeometry(self.left, self.top, self.width, self.height) # Set the dimension of the Window
        self.setStyleSheet("background-color: #2d2d2d") # Set the background color of the window to gray
        self.setMaximumHeight(self.height) # Constrain Dimensions
        self.setMaximumWidth(self.width)   # ^
        self.setMinimumHeight(self.height) # ^
        self.setMinimumWidth(self.width)   # ^

    def InitLayout(self):
        self.setLayout(self.vbox) # Set window layout to vertical
        self.vbox.setGeometry(QRect(self.left, self.top, self.width, self.height)) # Set geometry of layout
        self.vbox.setSpacing(10) # Set spacing of layout

class Worker1(QObject):
    finished = pyqtSignal()
    hc12Detected = pyqtSignal()
    hc12Baud = pyqtSignal()
    hc12Power = pyqtSignal()
    hc12Configured = pyqtSignal()
        
    def __init__(self, hc12, parent=None):
        QObject.__init__(self, parent=parent)
        self.hc12 = hc12
        self.continue_run = True
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)
        GPIO.output(17, GPIO.LOW)
                
    def do_work(self):
        while self.continue_run:
            QThread.sleep(1.5)
            self.hc12.write("AT")
            read = ''
            while read == '':
                read = self.hc12.read()
            if read == 'OK':
                read = ''
                QThread.sleep(1)
                self.hc12Detected.emit()
                self.hc12.write("AT+B9600")
                while read == '':
                    read = self.hc12.read()
                if read == 'OK+B9600':
                    read = ''
                    QThread.sleep(1.5)
                    self.hc12Baud.emit()
                    self.hc12.write("AT+P8")
                    while read == '':
                        read = self.hc12.read()
                    if read == 'OK+P8':
                        read = ''
                        QThread.sleep(2.3)
                        self.hc12Power.emit()
                        self.hc12.write("AT+C001")
                        while read == '':
                            read = self.hc12.read()
                        if read == 'OK+C001':
                            QThread.sleep(1.8)
                            self.hc12Configured.emit()
                            self.stop()
                        else:
                            print("ERROR SETTING CHANNEL!")
                    else:
                        print("ERROR SETTING POWER!")
                else:
                    print("ERROR SETTING BAUD RATE!")
            else:
                print("HC12 NOT COMMUNICATING!")
            
                        
    def stop(self):
        self.continue_run = False

class Worker2(QObject):
    finished = pyqtSignal()
    found = pyqtSignal()
    updateDistance = pyqtSignal(float)
        
    def __init__(self, hc12, parent=None):
        QObject.__init__(self, parent=parent)
        global root
        self.data = root.child('data')
        self.hc12 = hc12
        self.received = False
        self.continue_run = True
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)
        GPIO.output(17, GPIO.HIGH)
                
    def do_work(self):
        while self.continue_run:
            if self.received is False:
                data = ''
                while data is '':
                    data = self.hc12.read()
                print(data)
                if 'SOS' in data:
                    self.hc12.write('SOS')
                    self.received = True
                    self.found.emit()
                    QThread.sleep(1)
            else:
                self.hc12.write('$')
                print("Data Sent!")
                while data is '':
                    data = self.hc12.read()
                print("Data Received!")
                
                self.result = self.data.get()
                distance = self.result.get('distance')
                self.updateDistance.emit(distance)
                QThread.sleep(1)
            
                        
    def stop(self):
        self.continue_run = False

class StartPage(Window):
    switch_next = pyqtSignal(QWidget)
    stop_signal = pyqtSignal()
    
    def __init__(self, prev_window, hc12):
        super().__init__()
        self.hc12 = hc12
        self.thread = None
        self.worker = None
        self.movie1 = None
        self.movie2 = None
        self.lbl1 = None
        self.lbl2 = None
        self.lbl3 = None
        self.btn1 = None
        self.InitWindow()
        self.InitLayout()
        self.InitComponents()
        self.InitWorker()
        self.show()
                
    def InitComponents(self):
        self.lbl1 = QLabel("Checking Transceiver Module...")
        self.lbl1.setStyleSheet("color: #efefef; font: 25px; font-family: Sanserif")
        self.lbl1.setAlignment(Qt.AlignHCenter)
                
        self.lbl2 = QLabel(self) # placeholder for gif
        self.lbl2.setAlignment(Qt.AlignHCenter)
                
        self.lbl3 = QLabel("Trying to communicate with the transceiver...")
        self.lbl3.setAlignment(Qt.AlignHCenter)
        self.lbl3.setStyleSheet("color: #FAFAFA; font-family: Sanserif; font: 10px")
                
        self.movie1 = QMovie(self.userpath + '/salvavida/load.gif')
        self.movie1.setScaledSize(QtCore.QSize(200, 150))
                
        self.movie2 = QMovie(self.userpath + '/salvavida/check.gif')
        self.movie2.setScaledSize(QtCore.QSize(200, 150))
                
        self.lbl2.setMovie(self.movie1)
                
        self.movie1.start()
        
        self.btn1 = QPushButton("Please Wait...")
        self.btn1.setStyleSheet("font-family: Sanserif; font: 15px")
        self.btn1.setEnabled(False)
        self.btn1.clicked.connect(self.NextPage)
                
                
        self.setStyleSheet("background-color: #1c273a")
        self.vbox.addWidget(self.lbl1)
        self.vbox.addWidget(self.lbl2)
        self.vbox.addWidget(self.lbl3)
        self.vbox.addWidget(self.btn1)
                
    def InitWorker(self):
        self.thread = QThread(parent=self)
        self.worker = Worker1(self.hc12)
        
        self.stop_signal.connect(self.worker.stop)
        self.worker.moveToThread(self.thread)
        
        self.worker.hc12Detected.connect(self.Detected)
        self.worker.hc12Baud.connect(self.Baud)
        self.worker.hc12Power.connect(self.Power)
        self.worker.hc12Configured.connect(self.Configured)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.worker.stop)
        
        self.thread.started.connect(self.worker.do_work)
        
        self.thread.start()
        
    def Detected(self):
        self.lbl1.setText("Configuring HC12...")
        self.lbl3.setText("HC12 is Communicating.\nSetting Baud Rate...")
        
    def Baud(self):
        self.lbl3.setText("Baud Rate Change Success.\nSetting Power...")
        
    def Power(self):
        self.lbl3.setText("Transmitting Power set to 20dBm.\nSetting Channel...")
        
    def Configured(self):
        self.lbl1.setText("HC12 Successfully Configured!")
        self.lbl3.setText("Channel set to C001")
        self.lbl2.setMovie(self.movie2)
        self.movie2.start()
        self.setStyleSheet("background-color: #2d2d2d")
        self.btn1.setText("Continue")
        self.btn1.setEnabled(True)
        
    def NextPage(self):
        self.switch_next.emit(self)
                
    def closeEvent(self, event):
        self.hc12.stop()
        print("HC12 STOPPED")

class ReadPage(Window):
    stop_signal = pyqtSignal()
    
    def __init__(self, prev_window, hc12):
        super().__init__()
        self.hc12 = hc12
        self.lbl3 = None
        self.movie = None
        self.currentSys = 0
        self.InitWindow()
        self.InitLayout()
        self.val = 0.00
        self.lbl_distance = None
        self.InitComponents()
        self.InitWorker()
        self.show()
        if prev_window is not None:
            prev_window.hide()
                
    def InitWorker(self):
        self.thread = QThread(parent=self)
        self.worker = Worker2(self.hc12)
        
        self.stop_signal.connect(self.worker.stop)
        self.worker.moveToThread(self.thread)
        
        self.worker.updateDistance.connect(self.UpdateDistance)
        self.worker.found.connect(self.Found)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.worker.stop)
        
        self.thread.started.connect(self.worker.do_work)
        
        self.thread.start()
                
    def InitComponents(self):
        self.setStyleSheet("background-color: #2a2826")
        self.lbl1 = QLabel("Receiver: ")
        lbl2 = QLabel("System of Measurement")
        self.lbl_distance = QLabel("{:.2f}{}".format(self.val, "m"))
        self.lbl_distance.setText("Not Found")
        self.lbl_distance.setAlignment(Qt.AlignRight)
        
        self.lbl3 = QLabel()
        self.lbl3.setAlignment(Qt.AlignHCenter)
        
        self.movie = QMovie(self.userpath + '/salvavida/read.gif')
        self.movie.setScaledSize(QtCore.QSize(400, 300))
        
        self.lbl3.setMovie(self.movie)
        
        self.movie.start()
        
        btn1 = QPushButton("Meters", self)
        btn2 = QPushButton("Feet", self)
        btn3 = QPushButton("Nautical Miles", self)
        self.lbl1.setAlignment(Qt.AlignLeft)
        
        lbl2.setStyleSheet("color: #efefef; font: 20px; font-family: Sanserif")
        lbl2.setAlignment(Qt.AlignBottom)
        btn1.setStyleSheet("background-color: #ff6f00; color: #212121; font-family: Sanserif; font: 20px")
        btn2.setStyleSheet("background-color: #ff6f00; color: #212121; font: 20px; font-family: Sanserif")
        btn3.setStyleSheet("background-color: #ff6f00; color: #212121; font: 20px; font-family: Sanserif")
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        vbox2.setSpacing(1)
        
        btn1.clicked.connect(self.btn1Action)
        btn2.clicked.connect(self.btn2Action)
        btn3.clicked.connect(self.btn3Action)
        
        self.lbl1.setStyleSheet("color: #FAFAFA; font: 30px; font-family: Sanserif")
        self.lbl_distance.setStyleSheet("color: #FAFAFA; font: 30px; font-family: Sanserif")
        hbox1.addWidget(self.lbl1)
        hbox1.addWidget(self.lbl_distance)
        hbox2.addWidget(btn1)
        hbox2.addWidget(btn2)
        hbox2.addWidget(btn3)
        vbox1.addLayout(hbox1)
        vbox1.addWidget(self.lbl3)
        vbox2.addWidget(lbl2)
        vbox2.addLayout(hbox2)
        self.vbox.addLayout(vbox1)
        self.vbox.addLayout(vbox2)
        
    def updateVal(self):
        if(self.currentSys == 0):
            val = self.val
            if self.val < 0:
                self.lbl_distance.setText("<1{}".format("m"))
            else:
                self.lbl_distance.setText("{:.2f}{}".format(val, "m"))
        elif(self.currentSys == 1):
            val = self.val*3.28084
            self.lbl_distance.setText("{:.2f}{}".format(val, "ft"))
        elif(self.currentSys == 2):
            val = self.val*0.000539957
            self.lbl_distance.setText("{:.2f}{}".format(val, "Nm"))
                
    def btn1Action(self):
        self.currentSys = 0
        self.updateVal()
    def btn2Action(self):
        self.currentSys = 1
        self.updateVal()
    def btn3Action(self):
        self.currentSys = 2
        self.updateVal()
        
    def Found(self):
        self.lbl1.setText("Distance:")
        self.updateVal()
        
    def UpdateDistance(self, distance):
        self.val = distance
        self.updateVal()
                
    def closeEvent(self, event):
        self.hc12.stop()
        print("HC12 STOPPED")
        
        
class Controller:
    def __init__(self, ser):
        self.hc12 = ser
        self.StartPage = None # First page
        self.ReadPage = None
        
    def show_start(self):
        self.StartPage = StartPage(None, self.hc12)
        self.StartPage.switch_next.connect(self.show_read)

    def show_read(self, prev_window): # Show the read page (second window)
        self.ReadPage = ReadPage(prev_window, self.hc12) # pass startpage with the arduino listener
        


if __name__ == "__main__": 
    hc12 = SerialListener().start()
    app = QApplication(sys.argv) # Create an application object
    controller = Controller(hc12) # Start the controller class
    controller.show_start() # show the start page
    sys.exit(app.exec()) # Terminate the program when user exits ii.
