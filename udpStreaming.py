import socket
import os
import struct
import warnings
from tkinter import messagebox

warnings.filterwarnings("ignore")

IP = "127.0.0.1"
PORT = 1000
TIMEOUT = 5 # in seconds
BUFFER_SIZE = 68
isRecording = False

def stop_recording():
    global isRecording
    isRecording = False

def listen_udp(full_path):
    global isRecording
    isRecording = True
    file = open(f"{full_path}.csv", "wb+")

    try:
        end_point = (IP, PORT)

        # Initialize UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # udp_socket.settimeout(TIMEOUT)
        udp_socket.bind(end_point)
        receive_buffer_byte = bytearray(1024)

        print(f"Listening on {end_point}")
        # timer = Timer()

        # Acquisition loop
        while isRecording: 
            number_of_bytes_received, _ = udp_socket.recvfrom_into(receive_buffer_byte)
            # # timer.print_stopwatch()
            if number_of_bytes_received == BUFFER_SIZE:
                message_byte = receive_buffer_byte[:number_of_bytes_received]
                # unpacked_data = struct.unpack('17f', message_byte)
                file.write(message_byte)


    except Exception as ex:
        messagebox.showerror("Error", f"Error during UDP data acquisition: {ex}")
    finally:
        file.close()
        print("\nAcquisition has terminated")



if __name__ == "__main__":
    listen_udp("test")