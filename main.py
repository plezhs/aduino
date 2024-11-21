import pyfirmata
import time
import random
import socket

# Set up the Arduino board
board = pyfirmata.Arduino('COM6')

# Define the pins for the motor control
left_motor_forward = board.get_pin('d:3:o')
left_motor_backward = board.get_pin('d:4:o')
right_motor_forward = board.get_pin('d:5:o')
right_motor_backward = board.get_pin('d:6:o')

# Define the pin for the joystick button
joystick_button = board.get_pin('d:7:i')

# Define the pin for the stop button
stop_button = board.get_pin('d:8:i')

# Define the pins for the joystick axes
joystick_x = board.get_pin('a:0:i')
joystick_y = board.get_pin('a:1:i')

# Function to move the car forward
def move_forward(speed):
    left_motor_forward.write(speed)
    left_motor_backward.write(0)
    right_motor_forward.write(speed)
    right_motor_backward.write(0)

# Function to move the car backward
def move_backward(speed):
    left_motor_forward.write(0)
    left_motor_backward.write(speed)
    right_motor_forward.write(0)
    right_motor_backward.write(speed)

# Function to turn the car left
def turn_left(speed):
    left_motor_forward.write(0)
    left_motor_backward.write(speed)
    right_motor_forward.write(speed)
    right_motor_backward.write(0)

# Function to turn the car right
def turn_right(speed):
    left_motor_forward.write(speed)
    left_motor_backward.write(0)
    right_motor_forward.write(0)
    right_motor_backward.write(speed)

# Function to stop the car
def stop():
    left_motor_forward.write(0)
    left_motor_backward.write(0)
    right_motor_forward.write(0)
    right_motor_backward.write(0)

# Function to send data via serial
def send_data_via_serial(data):
    board.send_sysex(pyfirmata.STRING_DATA, pyfirmata.util.str_to_two_byte_iter(data))

# Set up the socket for wireless communication
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 12345))

# Main loop to control the car
car_running = False
recording = False
start_time = None
last_speed_change_time = None

while True:
    data, addr = sock.recvfrom(1024)
    command = data.decode('utf-8')

    if command == 'TOGGLE_CAR':
        car_running = not car_running
        if car_running:
            print("Car started")
            recording = True
            start_time = time.time()
            last_speed_change_time = time.time()
        else:
            stop()
            print("Car stopped")
        time.sleep(0.5)  # Debounce delay

    if command == 'STOP_RECORDING' and recording:
        recording = False
        end_time = time.time()
        elapsed_time = end_time - start_time
        data = f'Elapsed time: {elapsed_time}'
        send_data_via_serial(data)
        stop()
        print("Recording stopped and data sent")
        time.sleep(0.5)  # Debounce delay

    if car_running:
        x, y = map(float, command.split(','))
        current_time = time.time()

        if current_time - last_speed_change_time >= 3:
            speed = random.uniform(0.5, 1.0)  # Random speed between 50% and 100%
            last_speed_change_time = current_time

        if y > 0.5:
            move_forward(speed)
        elif y < -0.5:
            move_backward(speed)
        elif x > 0.5:
            turn_right(speed)
        elif x < -0.5:
            turn_left(speed)
        else:
            stop()
    time.sleep(0.1)