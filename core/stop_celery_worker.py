# stop_celery_worker.py

import os
import signal
import psutil

def get_celery_worker_pid():
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info.get('cmdline')
            if cmdline and 'celery' in cmdline and 'worker' in cmdline:
                return proc.info['pid']
    except Exception as e:
        print(f'Error finding Celery worker PID: {e}')
    return None

def stop_celery_worker():
    pid = get_celery_worker_pid()
    if pid:
        os.kill(pid, signal.SIGTERM)
        print('Successfully stopped Celery worker')
    else:
        print('Celery worker process not found')

if __name__ == "__main__":
    stop_celery_worker()
