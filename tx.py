from serial import Serial, serialutil
import time
from threading import Thread


class SerialListener:
    def __init__(self, baudrate=9600, timeout=0.5):
        
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

    def write(self, msg):
        self.ser.write(msg.encode())


if __name__ == "__main__":  # FOR DEBUGGING ONLY
    uno = SerialListener().start()
    uno.flush()
    try:
        uno.write('AT')
        print(uno.read())
    except KeyboardInterrupt:
        uno.stop()
        sql.close()
