import socket
import os
import struct
import threading
import warnings
from tkinter import messagebox

warnings.filterwarnings("ignore")

IP = "127.0.0.1"
PORT = 1000
TIMEOUT = 5 # in seconds
BUFFER_SIZE = 68
isRecording = threading.Event()

def stop_recording():
    isRecording.clear()

def listen_udp(full_path, user_name, user_id):
    isRecording.set()
    save_index = 1
    full_path = f"{os.getcwd()}{full_path}"
    print(full_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    while os.path.exists(f"{full_path}-{save_index}.csv"):
        save_index += 1
    
    full_path = f"{full_path}/{user_name}_{user_id}-{save_index}"

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
        while isRecording.is_set(): 
            number_of_bytes_received, _ = udp_socket.recvfrom_into(receive_buffer_byte)
            # # timer.print_stopwatch()
            if number_of_bytes_received > 0:
                message_byte = receive_buffer_byte[:number_of_bytes_received]

                file.write(message_byte)


    except Exception as ex:
        messagebox.showerror("Error", f"Error during UDP data acquisition: {ex}")
    finally:
        file.close()
        print("\nAcquisition has terminated")



if __name__ == "__main__":
    listen_udp("test", "A","1")