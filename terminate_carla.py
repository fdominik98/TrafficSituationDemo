import psutil

def terminate_process_by_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            proc.terminate()
            print(f"Terminated process {process_name} with PID {proc.info['pid']}")

process_name = "CarlaUE4-Win64-Shipping.exe"
terminate_process_by_name(process_name)