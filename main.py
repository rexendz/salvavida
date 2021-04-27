from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
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
        self.setStyleSheet("background-color: #424242") # Set the background color of the window to gray
        self.setMaximumHeight(self.height) # Constrain Dimensions
        self.setMaximumWidth(self.width)   # ^
        self.setMinimumHeight(self.height) # ^
        self.setMinimumWidth(self.width)   # ^

    def InitLayout(self):
        self.setLayout(self.vbox) # Set window layout to vertical
        self.vbox.setGeometry(QRect(self.left, self.top, self.width, self.height)) # Set geometry of layout
        self.vbox.setSpacing(10) # Set spacing of layout


class StartPage(Window):
	def __init__(self):
		super().__init__()
		self.InitWindow()
		self.InitLayout()
		self.InitComponents()
		self.show()
		
	def InitComponents(self):
		lbl1 = QLabel("Distance: ")
		lbl2 = QLabel("System of Measurement")
		lbl_distance = QLabel("{val}{sys}".format(val = "0.00", sys = "m"))
		lbl_distance.setAlignment(Qt.AlignRight)
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
		
		lbl1.setStyleSheet("color: #c43e00; font: 40px; font-family: Sanserif")
		lbl_distance.setStyleSheet("color: #c43e00; font: 40px; font-family: Sanserif")
		hbox1.addWidget(lbl1)
		hbox1.addWidget(lbl_distance)
		hbox2.addWidget(btn1)
		hbox2.addWidget(btn2)
		hbox2.addWidget(btn3)
		vbox1.addLayout(hbox1)
		vbox2.addWidget(lbl2)
		vbox2.addLayout(hbox2)
		self.vbox.addLayout(vbox1)
		self.vbox.addLayout(vbox2)
		
	def btn1Action(self):
		
	def btn2Action(self):
		
	def btn3Action(self):
	
	
class Controller:
    def __init__(self):
        self.StartPage = None # First page

    def show_start(self): # Show the start page (first window)
        self.StartPage = StartPage() # pass startpage with the arduino listener
        


if __name__ == "__main__": 
    app = QApplication(sys.argv) # Create an application object
    controller = Controller() # Start the controller class
    controller.show_start() # show the start page
    sys.exit(app.exec()) # Terminate the program when user exits ii.