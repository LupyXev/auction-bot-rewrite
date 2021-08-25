#Policy
"""
! : means command for the microservices main server
> : means requests for nonexisting Communication, request an verification output
$ : answer to an existing Communication

* : Means an issue/error
V : is validation (like when the server confirms request's receiving)

CLOSE : sent when a socket is closed by !DISCONNECT

Structure for answers (V or $):
V
"""

import socket
import threading
import logging
import logging.handlers
import time
import sys

PORT_SERV = 5050
PORT_CLIENT = 5051
HEADER = 64
HOST = "localhost"
FORMAT = "utf-8"


#init the handlers
r_file_handler_info = logging.handlers.RotatingFileHandler(
    filename='logs/MMS_info.log', 
    mode='a',
    maxBytes=5*1024*1024,
    backupCount=1,
    encoding="utf-8",
    delay=0
)
r_file_handler_info.setLevel(logging.INFO)

r_file_handler_debug = logging.handlers.RotatingFileHandler(
    filename='logs/MMS_debug.log', 
    mode='a',
    maxBytes=3*1024*1024,
    backupCount=1,
    encoding="utf-8",
    delay=0
)
r_file_handler_debug.setLevel(logging.DEBUG)

r_file_handler_all_warn = logging.handlers.RotatingFileHandler(
    filename='logs/all_warn.log', 
    mode='a',
    maxBytes=4*1024*1024,
    backupCount=1,
    encoding="utf-8",
    delay=0
)
r_file_handler_all_warn.setLevel(logging.WARNING)

#a "print" handler
stdout_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

r_file_handler_debug.setFormatter(formatter)
r_file_handler_info.setFormatter(formatter)
r_file_handler_all_warn.setFormatter(formatter)
stdout_handler.setFormatter(formatter)

def init_a_new_logger(name, lvl=logging.DEBUG):
    #init the logger
    logger = logging.getLogger(name)
    logger.setLevel(lvl)

    #linking the handlers
    logger.addHandler(r_file_handler_info)
    logger.addHandler(r_file_handler_debug)
    logger.addHandler(r_file_handler_all_warn)

    #adding a "print" handler
    logger.addHandler(stdout_handler)
    return logger


"""class CallableMicroServices:
    def __init__(self):
        self.dict = {}
        self.microservices_types = ("discord_bot", "hypixel_api_analysis")

    def get_microservice(self, microservice_name):
        if microservice_name in self.dict:
            return self.dict[microservice_name]
        else:
            return None #can be considered as False in the future
    
    def add_microservice(self, microservice_name, microservice_obj):
        if microservice_name in self.microservices_types:
            #will also overwrites the existing microservice with same name
            self.dict[microservice_name] = microservice_obj
            return True
        else:
            logger.error("CallableMicroServices -> add_microservices : not in the microservies_types list")
            return False
    
    def destroy_microservice(self, microservice_obj):
        key_to_destroy = None
        for key, value in self.dict.items():
            if value == microservice_obj:
                key_to_destroy = key

        if key_to_destroy is not None:
            self.dict.pop(key_to_destroy)"""


class Microservice:
    
    microservices_dict = {}
    microservices_types = ("discord_bot", "hypixel_api_analysis")

    @classmethod
    def get_microservice(cls, microservice_name):
        if microservice_name in cls.microservices_dict:
            return cls.microservices_dict[microservice_name]
        else:
            return None #can be considered as False in the future

    @classmethod
    def add_microservice(cls, microservice_name, send_socket=None):
        if microservice_name in cls.microservices_types:
            #will also overwrites the existing microservice with same name
            microservice = cls.get_microservice(microservice_name)
            if microservice is None:
                microservice = Microservice(microservice_name, send_socket)
            
            if send_socket is not None:
                microservice.change_socket(send_socket)
            
            microservice.alive = True
            return microservice
        else:
            logger.error("CallableMicroServices -> add_microservices : not in the microservies_types list")
            return None

    @classmethod
    def set_microservice_in_dict(cls, key, value):
        cls.microservices_dict[key] = value

    @classmethod
    def destroy_microservice(cls, microservice_obj):
        microservice_obj.close_socket()
        key_to_destroy = None
        for key, value in cls.microservices_dict.items():
            if value == microservice_obj:
                key_to_destroy = key

        if key_to_destroy is not None:
            cls.microservices_dict.pop(key_to_destroy)    

    def __init__(self, name, send_socket=None):
        logger.info(f"Initializing {name} microservice")
        self.name = name
        self.alive = True
        self.is_sending = False #if the socket is currently used

        self.send_socket = send_socket

        existing_microservice = self.get_microservice(name)
        if existing_microservice is not None:
            #so there is still an existing microservice objet for this one, overwrites it
            del(existing_microservice)
        self.set_microservice_in_dict(name, self)

    def destroy(self):
        self.destroy_microservice(self)
        self.alive = False
    
    def close_socket(self, socket_to_close="self"):
        if socket_to_close == "self":
            socket_to_close = self.send_socket
        if self.send_socket is socket_to_close:
            try:
                socket_to_close.send(str(len("CLOSE".encode(FORMAT))).encode(FORMAT))
                socket_to_close.send("CLOSE".encode(FORMAT))
            except:
                print("didn't succeeded in send CLOSE state")
            self.send_socket.close()
            self.send_socket = None
            del(socket_to_close)
    
    def change_socket(self, send_socket):
        if self.send_socket is not None: #overwrites
            self.send_socket.close()
        self.send_socket = send_socket
    
    """def add_communication(self, communication):
        if communication not in self.communications:
            self.communications.append(communication)"""
    
    def send(self, content: str):
        while self.is_sending:
            logger.warning(f"waiting for socket stop sending, for {self.name}")
            time.sleep(0.01)
        content = content.encode(FORMAT)
        self.is_sending = True
        self.send_socket.send(str(len(content)).encode(FORMAT))
        self.send_socket.send(content)
        self.is_sending = False

class Request: #single request
    def __init__(self, microservice_src: Microservice, microservice_dest: Microservice, data):
        self.microservice_src = microservice_src
        self.microservice_dest = microservice_dest
        self.data = data
    
    def get_src(self):
        if self.microservice_src.alive:
            return self.microservice_src
        else:
            return False

    def get_dest(self):
        if self.microservice_dest.alive:
            return self.microservice_dest
        else:
            return False

class Communication:
    last_id = -1
    id_to_communication_object = []

    @classmethod
    def new_id_and_add_to_list(cls, obj):
        new_id = cls.last_id + 1
        cls.last_id = new_id
        cls.id_to_communication_object.append(obj)
        return new_id

    def __init__(self, first_request=None):
        self.requests = []
        if first_request is not None:
            self.requests = [first_request]
        self.id = self.new_id_and_add_to_list(self)

    def add(self, request: Request):
        self.requests.append(request)
    
    def last_speaker(self):
        if len(self.requests) > 0:
            return self.requests[-1].get_src()
        return None


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT_SERV))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.bind((HOST, PORT_CLIENT))

def handle_server(conn, addr): #for clientmode, when the other side is mainly receiving and us mainly sending
    name = conn.recv(128).decode(FORMAT)
    microservice_obj = Microservice.get_microservice(name)

    if microservice_obj is None:
        conn.send("*BAD_NAME_OR_NOT_INITIALIZED".encode(FORMAT))
        logger.error(f"client mode bad name or not initialized : {name}")
    else:
        #set this socket for commands to this microservice
        microservice_obj.change_socket(conn)
        #Confirm the initialization
        conn.send(name.encode(FORMAT))

        print(f"{microservice_obj.name} CLIENTmode initialized")


def handle_client(conn, addr):
    #must send its microservice type
    name = conn.recv(128).decode(FORMAT)
    microservice_obj = Microservice.add_microservice(name)

    if microservice_obj is None:
        conn.send("*BAD_NAME".encode(FORMAT))
        logger.error(f"Init bad name : {name}")
        return
    #Confirm the initialization
    conn.send(name.encode(FORMAT))

    print(f"{microservice_obj.name} SERVERmode initialized")

    while True:
        try:
            msg_length = conn.recv(HEADER)
        except:
            break

        msg_length = msg_length.decode(FORMAT)
        if msg_length: #handle None received
            msg_length = int(msg_length)
            print("taille reçue", msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            print(f"reçu {msg}")

            msgSplitted = msg.split(" ")
            if msg[0] == "!": #main server commands
                if msg == "!DISCONNECT":
                    print("Disconnected by customer")
                    microservice_obj.destroy()
                    break
                else:
                    conn.send("*BAD_SERVER_COMMAND".encode(FORMAT))
                    logger.warn(f"bad server command : {msg} from {name}")
            elif msg[0] == "$": #output to an existing Communication
                #not implemented yet
                pass
            elif msg[0] == ">": 
                dest = Microservice.get_microservice(msgSplitted[0][1:])
                if dest is None:
                    conn.send("*BAD_DEST_NAME".encode(FORMAT))
                    logger.error(f"Bad destination name : {msgSplitted[0][1:]} from {name}")
                elif dest.alive is False:
                    conn.send("*DIED_DEST".encode(FORMAT))
                    logger.warning(f"Died dest : {msgSplitted[0][1:]} asked from {name}")
                elif dest.send_socket is None:
                    conn.send("*NO_SOCKET_DEST".encode(FORMAT))
                    logger.warning(f"No socket dest : {msgSplitted[0][1:]} asked from {name}")
                else:
                    data = msg[len(msgSplitted[0]) + 1:]
                    #cur_request = Request(microservice_obj, dest, data)

                    #send the request
                    try:
                        dest.send(data)
                    except:
                        conn.send("*DEST_SOCKET_WORKING_ERR".encode(FORMAT))
                        logger.warning(f"Error when sending data (socket closed ?) to : {msgSplitted[0][1:]} asked from {name}\n{data}")

                    #send verification to request's source
                    conn.send(f"V{msg_length}".encode(FORMAT))
            else:
                conn.send("*BAD_PREFIX".encode(FORMAT))
                logger.warn(f"no correct prefix specified : {msg} from {name}")
        
        else:
            print("None received, closing servermode loop")
            break
    
    print(f"microservice {name}'s request port (our SERVERmode) disconnected")

def start_servermode():
    server.listen()
    print("server is listening...")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        logger.debug(f"new servermode connexion started")

def start_clientmode():
    client.listen()
    print("client is listening...")
    while True:
        conn, addr = client.accept()
        thread = threading.Thread(target=handle_server, args=(conn, addr))
        thread.start()
        logger.debug("new clientmode connexion started")

thread_servermode = threading.Thread(target=start_servermode)
thread_servermode.start()
start_clientmode()