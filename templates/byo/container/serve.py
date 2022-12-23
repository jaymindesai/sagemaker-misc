# This file starts the inference server. It starts nginx and gunicorn with the correct configurations and then simply
# waits until gunicorn exits.
#
# The flask server is specified to be the app object in wsgi.py
#
# We set the following parameters:
#
# Parameter                Environment Variable              Default Value
# ---------                --------------------              -------------
# number of workers        MODEL_SERVER_WORKERS              the number of CPU cores
# number of threads        MODEL_SERVER_THREADS_PER_WORKERS  2
# timeout                  MODEL_SERVER_TIMEOUT              60 seconds
# log level                LOG_LEVEL                         INFO

import multiprocessing
import os
import signal
import subprocess
import sys
import logging.config

# Model config
_model_server_timeout = os.environ.get('MODEL_SERVER_TIMEOUT', 60)
_model_server_workers = int(os.environ.get('MODEL_SERVER_WORKERS', multiprocessing.cpu_count()))
_num_threads_per_worker = int(os.environ.get('MODEL_SERVER_THREADS_PER_WORKERS', 2))
_worker_class = "gthread"
_log_level = os.environ.get('LOG_LEVEL', 'INFO')


def start_server():
    logging.info("Starting inference server")
    logging.info(
        "Gunicorn config: workers={}, worker_class={}, threads_per_worker={}, timeout={}".format(
            _model_server_workers, _worker_class, _num_threads_per_worker, _model_server_timeout))

    # Link the log streams to stdout/err, so they will be logged to the containers logs
    subprocess.check_call(['ln', '-sf', '/dev/stdout', '/var/log/nginx/access.log'])
    subprocess.check_call(['ln', '-sf', '/dev/stderr', '/var/log/nginx/error.log'])

    nginx = subprocess.Popen(['nginx', '-c', "/opt/program/nginx.conf"])
    gunicorn = subprocess.Popen(['gunicorn',
                                 '--bind', 'unix:/tmp/gunicorn.sock',
                                 '--timeout', str(_model_server_timeout),
                                 '--worker-class', _worker_class,
                                 '--workers', str(_model_server_workers),
                                 '--threads', str(_num_threads_per_worker),
                                 '--log-level', _log_level,
                                 '--preload',
                                 'inference:app'])

    signal.signal(signal.SIGTERM, lambda: _sigterm_handler(nginx.pid, gunicorn.pid))

    # If either subprocess exits, so do we
    pids = {nginx.pid, gunicorn.pid}
    while True:
        pid, _ = os.wait()
        if pid in pids:
            break

    _sigterm_handler(nginx.pid, gunicorn.pid)
    logging.info("Exiting inference server")


def _sigterm_handler(nginx_pid, gunicorn_pid):
    try:
        os.kill(nginx_pid, signal.SIGQUIT)
    except OSError:
        pass
    try:
        os.kill(gunicorn_pid, signal.SIGTERM)
    except OSError:
        pass
    sys.exit(0)


if __name__ == '__main__':
    start_server()
