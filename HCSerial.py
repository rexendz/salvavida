from serial import Serial, serialutil
from serial.serialutil import SerialException
import time
from threading import Thread
import RPi.GPIO as GPIO


class SerialListener:
    def __init__(self, baudrate=9600, timeout=0.005):
        self.run = True
        self.ser = Serial('/dev/serial0', baudrate, timeout=timeout)
        self.stopped = False
        self.paused = False
        self.stream = ''
        time.sleep(1)  # Wait for serial buffer to reset
        print("Serial Started")

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while self.run:
            if not self.paused:
                if self.stopped:
                    self.ser.close()
                    self.run = False
                    print("Serial Thread Stopped")
                    print("Serial Port Closed")
                try:
                    try:
                        self.stream = self.ser.readline().decode('utf-8')
                    except:
                        self.stream = self.ser.readline().decode('ascii')
                    self.stream = self.stream.rstrip()
                except SerialException:
                    self.run = False

    def stop(self):
        self.paused = False
        self.stopped = True
        self.run = False

    def resume(self):
        self.paused = False
        self.run = True

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


if __name__ == "__main__":  # FOR DEBUGGING ONLY
    uno = SerialListener().start()
    uno.flush()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    GPIO.output(17, GPIO.LOW)
    data = ''
    print("HC12 SET TO CONFIG MODE")
    try:
        while True:
            time.sleep(1)
            GPIO.output(17, GPIO.LOW)
            data = input("\n")
            uno.write(data)
            read = ''
            while read == '':
                read = uno.read()
            print(read)
            
    except KeyboardInterrupt:
        uno.stop()
