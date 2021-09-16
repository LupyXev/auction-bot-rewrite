from socket import socket, AF_INET, SOCK_STREAM
from time import time, sleep
from json import loads, dumps

class MicroserviceSocket:
    HEADER = 64
    HOST = "localhost"
    FORMAT = "utf-8"

    MAIN_MICROSERVICE_REQ = "!"
    FIRST_REQUEST = ">"
    EXISTING_REQUEST = "$"

    def __init__(self, linked_microservice, logger, port):
        self.logger = logger
        linked_microservice.receiver = self
        self.microservice = linked_microservice
        self.socket = socket(AF_INET, SOCK_STREAM)

        #init the connection
        logger.info(f"Starting init to Microservice main server, with microservice name {self.microservice.name}")
        self.socket.connect((self.HOST, port))
        self.socket.send(self.microservice.name.encode(self.FORMAT))
        resp = self.socket.recv(128).decode(self.FORMAT)

        if resp != self.microservice.name: #bad initialization
            logger.error(f"Bad initialization, server answered with {resp}")
    
    def sock_receive(self, req_lenght):
        try:
            return self.socket.recv(req_lenght)
        except:
            self.logger.error(f"Error when receiving, connection closed ?, linked microservice : {self.microservice.name}")
            return ""
    
    def sock_send(self, req_content):
        try:
            return self.socket.send(req_content)
        except:
            self.logger.error(f"Error when sending, connection closed ?, linked microservice : {self.microservice.name}")
            return ""

class MicroserviceSender(MicroserviceSocket):
    PORT = 5050
    def __init__(self, linked_microservice, logger):
        super().__init__(linked_microservice, logger, self.PORT)
        linked_microservice.initialized_to_main_microservices_server = True #should be initialized to main microservices serv
        linked_microservice.sender = self
    
    def send_to_main_microservice_server(self, command):
        req_content = f"!{command}".encode(self.FORMAT)
        req_lenght = str(len(req_content)).encode(self.FORMAT)
        
        self.sock_send(req_lenght)
        self.sock_receive(self.HEADER) #waiting the server to say "ok, I've got the req_lenght"
        self.sock_send(req_content)
        resp_lenght = int(self.sock_receive(self.HEADER).decode(self.FORMAT))
        
        return self.sock_receive(resp_lenght).decode(self.FORMAT) #the verification resp

    def send_to_a_microservice(self, req_type, dest, command, args={}, req_id=None):
        sleep(0.005) #to limit IDs errors (with same id) and spamming
        if req_id is None:
            req_id=f"{self.microservice.prefix_id}{round(time(), 3)}"
        args["request_id"] = req_id
        req_content = f"{req_type}{dest} {command} {dumps(args)}".encode(self.FORMAT)
        self.logger.debug(f"sending {req_content}")
        
        req_lenght = str(len(req_content)).encode(self.FORMAT)
        
        self.sock_send(req_lenght)
        self.sock_receive(self.HEADER) #waiting the server to say "ok, I've got the req_lenght"
        #self.logger.debug(f"Sending request {req_type}{dest} {command} {dumps(args)}")
        self.sock_send(req_content)
        resp_lenght = self.sock_receive(self.HEADER).decode(self.FORMAT)
        try:
            resp_lenght = int(resp_lenght)
        except:
            self.logger.error(f"Can't take an int value for the resp_lenght of the verification, got {resp_lenght}")
            resp_lenght = self.HEADER
        self.sock_send(str(resp_lenght).encode(self.FORMAT)) #to say to the server that you've got the verif lenght

        verif_code = self.sock_receive(resp_lenght).decode(self.FORMAT)
        good_verif_code = True if verif_code[0] == "V" else False

        if good_verif_code:
            try:
                verif_code_lenght_received = int(verif_code[1:])
                if verif_code_lenght_received != req_lenght:
                    good_verif_code = False
                #else: no error
            except:
                good_verif_code = False

        return good_verif_code, verif_code #the verification resp

class MicroserviceReceiver(MicroserviceSocket):
    PORT = 5051
    def __init__(self, linked_microservice, logger):
        
        super().__init__(linked_microservice, logger, self.PORT)
        linked_microservice.receiver = self
        if not linked_microservice.initialized_to_main_microservices_server:
            logger.warning(f"Tried to create a MicroserviceReceiver but Microservice is not initialized to main microservices server. name : {linked_microservice.name}")
            self.connection_alive = False
        else:
            self.connection_alive = True

    def listen(self):#should be called from a loop
        req_lenght = self.sock_receive(self.HEADER).decode(self.FORMAT)

        if not req_lenght: #handle None or any obj meaning the connection is no longer alive
            self.connection_alive = False
            return None #connection closed
        req_lenght = int(req_lenght)
        
        self.logger.debug(f"Got a req_lenght : {req_lenght}")
        self.sock_send(str(req_lenght).encode(self.FORMAT)) #to say to the server that we've got the req lenght

        req = self.sock_receive(req_lenght).decode(self.FORMAT)
        self.logger.debug(f"Got a request : {req}")
        if req == "CLOSE":
            self.microservice.initialized_to_main_microservices_server = False
        req_splitted = req.split()
        args = {}
        if len(req_splitted) > 1: args = loads(req[len(req_splitted[0]):]) #if there is args

        req_dict = {"command": req_splitted[0], "args": args}
        
        return req_dict

class Microservice:
    def __init__(self, name, prefix_id, useful_objs:dict):
        self.name = name
        self.prefix_id = prefix_id
        self.requests_to_execute = {} #id: command_to_execute
        self.initialized_to_main_microservices_server = False
        self.useful_objs = useful_objs

class Queue:
    def __init__(self, logger):
        self.logger = logger
        self.queue_dict_by_request_id = {}
        self.queue = []
    
    def add(self, request_id: str, data:any):
        if request_id in self.queue_dict_by_request_id:
            self.logger.warning(f"Trying to add a request in Queue obj but there is already a request with same id : {request_id}, data : {data}")
        self.queue_dict_by_request_id[request_id] = data
        self.queue.append(request_id)

    def get_prior_and_delete_it(self):
        request_id = self.queue.pop(0)
        return self.queue_dict_by_request_id.pop(request_id)

#--- Test Zone ---
"""
import logging, logging.handlers, sys
from time import sleep

#init the handlers
#a "print" handler
stdout_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stdout_handler.setFormatter(formatter)

def init_a_new_logger(name, lvl=logging.DEBUG):
    #init the logger
    logger = logging.getLogger(name)
    logger.setLevel(lvl)

    #adding a "print" handler
    logger.addHandler(stdout_handler)
    return logger

m = Microservice("discord_bot", 'D')
s = MicroserviceSender(m, init_a_new_logger("d"))
s.send_to_main_microservice_server("DISCONNECT")
sleep(5)"""