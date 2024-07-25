import psutil
import os
import signal

def find_and_terminate_process(command):
    """
    Find and terminate the process running the given command.
    """
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and command in " ".join(cmdline):
                print(f"Found process {proc.info['name']} (PID: {proc.info['pid']}) running command: {command}")
                os.kill(proc.info['pid'], signal.SIGTERM)
                print(f"Sent SIGTERM to process {proc.info['pid']}")
                return
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    print("No running process found with the specified command.")

if __name__ == "__main__":
    command_to_find = "manage.py consume_messages"  # Replace 'your_command' with your actual command
    find_and_terminate_process(command_to_find)
