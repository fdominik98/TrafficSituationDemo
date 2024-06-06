import subprocess
import sys
import os
import signal

def run_exe_with_args(exe_path, args):
    try:
        # Create the command to run the exe with arguments
        command = [exe_path] + args

        # Start the subprocess
        process = subprocess.Popen(command)

        # Define the signal handler to terminate the subprocess
        def terminate_process(signal_number, frame):
            print("Terminating the process...")
            process.terminate()
            process.wait()
            sys.exit(0)

        # Register the signal handler for termination signals
        signal.signal(signal.SIGINT, terminate_process)
        signal.signal(signal.SIGTERM, terminate_process)

        # Wait for the process to complete
        process.wait()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait()

if __name__ == "__main__": 
    run_exe_with_args('CARLA/CARLAUE4.exe', ['-RenderOffscreen', '-carla-world-port=2001', '-quality-level=Epic'])