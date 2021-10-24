import logging
import logging.handlers
import sys
from os import getcwd

if getcwd() == "C:\\Users\\lucie\\Documents\\Projets code\\auction-bot-rewrite":
    logs_directory = "C:/Users/lucie/Documents/Projets code/auction-bot-rewrite/logs/"
else:
    logs_directory = "/home/ubuntu/logs/"

#init the handlers
r_file_handler_info = logging.handlers.RotatingFileHandler(
    filename=logs_directory + 'HAM_info.log', 
    mode='a',
    maxBytes=5*1024*1024,
    backupCount=1,
    encoding="utf-8",
    delay=0
)
r_file_handler_info.setLevel(logging.INFO)


r_file_handler_debug = logging.handlers.RotatingFileHandler(
    filename=logs_directory + 'HAM_debug.log', 
    mode='a',
    maxBytes=3*1024*1024,
    backupCount=1,
    encoding="utf-8",
    delay=0
)
r_file_handler_debug.setLevel(logging.DEBUG)

r_file_handler_all_warn = logging.handlers.RotatingFileHandler(
    filename=logs_directory + 'all_warn.log', 
    mode='a',
    maxBytes=4*1024*1024,
    backupCount=1,
    encoding="utf-8",
    delay=0
)
r_file_handler_all_warn.setLevel(logging.WARNING)

socket_handler = logging.handlers.SocketHandler("localhost", 5060)
socket_handler.setLevel(logging.WARNING)

#a "print" handler
stdout_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

r_file_handler_debug.setFormatter(formatter)
r_file_handler_info.setFormatter(formatter)
r_file_handler_all_warn.setFormatter(formatter)
stdout_handler.setFormatter(formatter)
socket_handler.setFormatter(formatter)

def init_a_new_logger(name, lvl=logging.DEBUG):
    #init the logger
    logger = logging.getLogger(name)
    logger.setLevel(lvl)

    #linking the handlers
    logger.addHandler(r_file_handler_info)
    logger.addHandler(r_file_handler_debug)
    logger.addHandler(r_file_handler_all_warn)
    logger.addHandler(socket_handler)

    #adding a "print" handler
    logger.addHandler(stdout_handler)
    return logger