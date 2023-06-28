from logging.handlers import SysLogHandler
import logging
import sys

'''
If using SysLogHandler (accurate severity) and running rlpi as systemd service, set:
    StandardOutput=null
    StandardError=null
or disable the StreamHandler to avoid double logs.
'''
def logConfig(loggername):
    log = logging.getLogger(loggername)
    log.setLevel(logging.DEBUG)
    logformat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Console output
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(logging.INFO)
    log.addHandler(console_handler)

    # Linux syslog output. Use address='/var/run/syslog' on Tim Apple systems
    if sys.platform.startswith('linux'):
        syslog_handler = SysLogHandler(
            facility=SysLogHandler.LOG_DAEMON,
            address='/dev/log'
        )
        log.addHandler(syslog_handler)

    # Dedicated log file output
    file_handler = logging.FileHandler('rlpi.log', mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logformat)
    log.addHandler(file_handler)

    log.propagate = False

    return log


def logWipe():
    with open('rlpi.log', 'w') as wipe:
        pass


log = logConfig('rlpi_logger')
