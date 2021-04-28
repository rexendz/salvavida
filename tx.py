from serial import Serial, serialutil
import time
from threading import Thread
import RPi.GPIO as GPIO


class SerialListener:
    def __init__(self, baudrate=9600, timeout=0.5):
        
        self.ser = Serial('/dev/serial0', baudrate, timeout=timeout)
        self.starting = time.time_ns()
        self.ending = time.time_ns()
        self.stopped = False
        self.paused = False
        self.stream = ''
        time.sleep(1)  # Wait for serial buffer to reset
        print("Serial Started")

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if not self.paused:
                if self.stopped:
                    self.ser.close()
                    print("Serial Thread Stopped")
                    print("Serial Port Closed")
                    self.paused = True
                try:
                    self.stream = self.ser.readline().decode('utf-8')
                except:
                    self.stream = self.ser.readline().decode('ascii')
                self.stream = self.stream.rstrip()
                if self.stream is not '':
                    print("HC12: " + self.stream + '\n')
                    self.ending = time.time_ns()

    def stop(self):
        self.paused = False
        self.stopped = True

    def resume(self):
        self.paused = False

    def pause(self):
        self.paused = True

    def flush(self):
        self.ser.flush()

    def SerialAvailable(self):
        return self.ser.inWaiting()

    def readDistance(self):  # Deprecated as distance is now read within Arduino
        try:
            return float(self.stream)
        except:
            return -1  # Returns -1 if there is an error in reading

    def read(self):
        return self.stream
        
    def getStart(self):
        return self.starting
        
    def getEnd(self):
        return self.ending

    def write(self, msg):
        self.ser.write(msg.encode())
        self.starting = time.time_ns()


if __name__ == "__main__":  # FOR DEBUGGING ONLY
    uno = SerialListener().start()
    uno.flush()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    GPIO.output(17, GPIO.LOW)
    print("HC12 SET TO CONFIG MODE")
    try:
        while True:
            starting, ending = 0, 0
            data = input("\n")
            GPIO.output(17, GPIO.HIGH)
            print("GPIO SET TO TRANSMIT MODE")
            ending = uno.getEnd()
            uno.write('s')
            starting = uno.getStart()
            print("MESSAGE 's' HAS BEEN TRANSMITTED")
            while(ending == uno.getEnd()):
                None
            ending = uno.getEnd()
            print("Starting = {}\nEnding = {}\n".format(starting, ending))
            diff = ending - starting
            print("Diff = {}".format(diff))
            distance = (0.0000000003 * diff)/2
            print("Distance = {}m".format(distance))
    except KeyboardInterrupt:
        uno.stop()
