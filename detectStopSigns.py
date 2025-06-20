import cv2
import imutils
import time
import serial
import argparse
from serial.tools import list_ports

class StopSignDetector:
    def __init__(self, cascade_path, com_port=None, baud_rate=9600):
        # Load Haar cascade classifier
        self.stop_sign_cascade = cv2.CascadeClassifier(cascade_path)
        if self.stop_sign_cascade.empty():
            raise ValueError(f"Could not load cascade classifier from {cascade_path}")
        
        # Initialize serial communication
        self.serial_port = None
        if com_port:
            try:
                self.serial_port = serial.Serial(com_port, baud_rate, timeout=1)
                time.sleep(2)  # Wait for connection to establish
            except serial.SerialException as e:
                print(f"Warning: Could not open serial port {com_port}: {e}")
        
        # Detection parameters
        self.detection_window = 3  # Seconds to send '1' after detection
        self.last_detection_time = 0
        self.detected = False
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")
    
    def detect_stop_sign(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        stop_signs = self.stop_sign_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return len(stop_signs) > 0, stop_signs
    
    def process_frame(self, frame):
        # Resize frame for processing
        frame = imutils.resize(frame, width=500)
        target_image = frame.copy()
        
        # Detect stop signs
        has_stop_sign, stop_signs = self.detect_stop_sign(frame)
        current_time = time.time()
        
        if has_stop_sign:
            self.detected = True
            self.last_detection_time = current_time
            print("1")  # Console log 1 when detected
            
            # Draw rectangles around detected stop signs
            for (x, y, w, h) in stop_signs:
                cv2.rectangle(target_image, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(target_image, "STOP SIGN", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Send stop command if serial is connected
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.write(b'1')
        else:
            # Check if we're still within the detection window
            if current_time - self.last_detection_time < self.detection_window:
                print("1")  # Keep logging 1 during detection window
                if self.serial_port and self.serial_port.is_open:
                    self.serial_port.write(b'1')
            else:
                self.detected = False
                print("0")  # Console log 0 when not detected
                if self.serial_port and self.serial_port.is_open:
                    self.serial_port.write(b'0')
        
        return target_image
    
    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Can't receive frame. Exiting...")
                    break
                
                processed_frame = self.process_frame(frame)
                cv2.imshow('Stop Sign Detector', processed_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()

def list_serial_ports():
    """List available serial ports"""
    ports = list_ports.comports()
    if not ports:
        print("No serial ports found!")
    else:
        print("Available serial ports:")
        for i, port in enumerate(ports):
            print(f"{i+1}. {port.device} - {port.description}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stop Sign Detector with Haar Cascade")
    parser.add_argument("-c", "--cascade", required=True, help="Path to the Haar cascade XML file")
    parser.add_argument("-p", "--comport", help="COM port for UART communication")
    parser.add_argument("-l", "--list-ports", action="store_true", help="List available serial ports")
    
    args = parser.parse_args()
    
    if args.list_ports:
        list_serial_ports()
        exit()
    
    try:
        detector = StopSignDetector(args.cascade, args.comport)
        detector.run()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)