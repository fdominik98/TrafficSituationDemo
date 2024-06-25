
def run_exe_with_args(exe_path, args):
    import subprocess
    import sys
    import signal
    try:
        # Create the command to run the exe with arguments
        command = [exe_path] + args

        # Start the subprocess with stdout and stderr redirected
        process = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr)

        # Define the signal handler to terminate the subprocess
        def terminate_process(signal_number, frame):
            print("Terminating the process...")
            process.terminate()
            process.wait()
            sys.exit(0)

        # Register the signal handler for termination signals
        signal.signal(signal.SIGINT, terminate_process)
        signal.signal(signal.SIGTERM, terminate_process)

    except Exception as e:
        print(f"An error occurred: {e}")


def run_carla():
    run_exe_with_args('CARLA/CARLAUE4.exe', ['-carla-world-port=2001', '-quality-level=Epic'])
    wait_for_server('127.0.0.1', '2001')


def terminate_process_by_name(process_name):
    import psutil
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            proc.terminate()
            print(f"Terminated process {process_name} with PID {proc.info['pid']}")

def terminate_carla():
    terminate_process_by_name("CarlaUE4-Win64-Shipping.exe")


def wait_for_server(host, port, timeout=1):
    import socket
    import time
    while True:
        try:
            with socket.create_connection((host, port), timeout):
                print(f"Connected to {host} on port {port}")
                return True
        except (OSError, ConnectionRefusedError):
            print(f"Waiting for server on {host}:{port}...")
            time.sleep(timeout)  # Wait before trying again

import os

def get_files_in_folder(folder_path):
    file_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append((file_path, file))
    return file_paths

