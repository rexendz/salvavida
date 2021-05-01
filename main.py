from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from HCSerial import SerialListener
import RPi.GPIO as GPIO
import os
import sys




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
        self.setStyleSheet("background-color: #1c273a") # Set the background color of the window to gray
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
	
    def __init__(self, hc12, parent=None):
        QObject.__init__(self, parent=parent)
        self.hc12 = hc12
        self.continue_run = True
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)
        GPIO.output(17, GPIO.LOW)
		
    def do_work(self):
        while self.continue_run:
            self.hc12.write("AT")
            read = ''
        while read == '':
		read = self.hc12.read()
	    if read == 'OK':
		self.hc12Detected.emit()
		print("OK!")
		self.stop()
	    else:
		QThread.sleep(0.5)
	    
			
    def stop(self):
	self.continue_run = False

class StartPage(Window):
    def __init__(self, hc12):
	super().__init__()
	self.hc12 = hc12
	self.thread = None
	self.worker = None
	self.InitWindow()
	self.InitLayout()
	self.InitComponents()
	self.InitWorker()
	self.show()
		
    def InitComponents(self):
	lbl1 = QLabel("Checking Transceiver Module...")
	lbl1.setStyleSheet("color: #efefef; font: 20px; font-family: Sanserif")
	lbl1.setAlignment(Qt.AlignHCenter)
		
	lbl2 = QLabel(self) # placeholder for gif
	lbl2.setAlignment(Qt.AlignHCenter)
		
	lbl3 = QLabel("Attempting communication with the Transceiver Module")
	lbl3.setStyleSheet("color: #FAFAFA; font-family: Sanserif; font: 15px")
		
	movie1 = QMovie(self.userpath + '/salvavida/load.gif')
	movie1.setScaledSize(QtCore.QSize(150, 150))
		
	movie2 = QMovie(self.userpath + '/salvavida/ok.gif')
	movie2.setScaledSize(QtCore.QSize(150, 150))
		
	lbl2.setMovie(movie1)
		
	movie1.start()
		
		
	self.vbox.addWidget(lbl1)
	self.vbox.addWidget(lbl2)
	self.vbox.addWidget(lbl3)
		
    def InitWorker(self):
	self.thread = QThread(parent=self)
	self.worker = Worker1(self.hc12)
	
	self.stop_signal.connect(self.worker.stop)
	self.worker.moveToThread(self.thread)
	
	self.worker.hc12Detected.connect(self.NextPage)
	
	self.worker.finished.connect(self.thread.quit)
	self.worker.finished.connect(self.worker.deleteLater)
	self.thread.finished.connect(self.thread.deleteLater)
	self.thread.finished.connect(self.worket.stop)
	
	self.thread.started.connect(self.worker.do_work)
	
	self.thread.start()
		
    def closeEvent(self, event):
	self.hc12.stop()
	print("HC12 STOPPED")

class ReadPage(Window):
    def __init__(self):
	super().__init__()
	self.InitWindow()
	self.InitLayout()
	self.val = 9999999999
	self.lbl_distance = None
	self.InitComponents()
	self.show()
		
    def InitComponents(self):
	lbl1 = QLabel("Distance: ")
	lbl2 = QLabel("System of Measurement")
	self.lbl_distance = QLabel("{:.2f}{}".format(self.val, "m"))
	self.lbl_distance.setAlignment(Qt.AlignRight)
	btn1 = QPushButton("Meters", self)
	btn2 = QPushButton("Feet", self)
	btn3 = QPushButton("Nautical Miles", self)
	lbl1.setAlignment(Qt.AlignLeft)
	
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
	
	lbl1.setStyleSheet("color: #c43e00; font: 30px; font-family: Sanserif")
	self.lbl_distance.setStyleSheet("color: #c43e00; font: 30px; font-family: Sanserif")
	hbox1.addWidget(lbl1)
	hbox1.addWidget(self.lbl_distance)
	hbox2.addWidget(btn1)
	hbox2.addWidget(btn2)
	hbox2.addWidget(btn3)
	vbox1.addLayout(hbox1)
	vbox2.addWidget(lbl2)
	vbox2.addLayout(hbox2)
	self.vbox.addLayout(vbox1)
	self.vbox.addLayout(vbox2)
		
    def btn1Action(self):
	val = self.val
	self.lbl_distance.setText("{:.2f}{}".format(val, "m"))
    def btn2Action(self):
	val = self.val*3.28084
	self.lbl_distance.setText("{:.2f}{}".format(val, "ft"))
    def btn3Action(self):
	val = self.val*0.000539957
	self.lbl_distance.setText("{:.2f}{}".format(val, "Nm"))
	
	
class Controller:
    def __init__(self, ser):
        self.hc12 = ser
        self.StartPage = None # First page
        self.ReadPage = None
	
    def show_start(self):
        self.StartPage = StartPage(self.hc12)

    def show_read(self): # Show the read page (second window)
        self.ReadPage = ReadPage() # pass startpage with the arduino listener
        


if __name__ == "__main__": 
    hc12 = SerialListener().start()
    app = QApplication(sys.argv) # Create an application object
    controller = Controller(hc12) # Start the controller class
    controller.show_start() # show the start page
    sys.exit(app.exec()) # Terminate the program when user exits ii.
