#!/usr/bin/env python3

# Imports for Job Handling
import http.client
import pickle
import time
import sshtunnel
import signal
import sys
import threading
import os
import job
import requests
import hashlib
import paramiko
from io import StringIO
import multiprocessing

import logging

# Imports for Job Processing
import clientjobexec

# Debug Bool
dodebug = True

#Multiprocessing Consts
mp_max = multiprocessing.cpu_count()-1

# SSH TUNNEL CONNECTION VARS
hostip = "jcwcopg.ddns.net"
user = "tunnel"
port = 55557
server_port = 60000
local_port = 8000

# Current Dir Finder
basepath = __file__
currentdir = ""
for i in range(len(basepath.split("/"))-1):
    currentdir = currentdir + basepath.split("/")[i] + "/"

# Job Vars
inprogress_jobs = []
completed_jobs = []
jobs_completed = 0
mp_availible_threads = multiprocessing.cpu_count()-1

# Identification Vars
# pgrmdir = __file__ + "/../"
# idfile = pgrmdir + "id.txt"
ident = None
identcreated = False

class exitsig():
    def __init__(self):
        self.cleanupfxnlist = []
        self.addcleanupfxn(self.printclosing)

    def addcleanupfxn(self, fxn):
        if callable(fxn):
            self.cleanupfxnlist.append(fxn)

    def printclosing(self):
        logger(1, f"Program Exiting...")

    def signal_handler(self, signal, frame):
        for fxn in self.cleanupfxnlist:
            fxn()
        sys.exit(0)

class keepalive(threading.Thread):
    def __init__(self):
        super(keepalive, self).__init__()
        self.running = False
        self.program_running = True
        self.timesfailed = 0

    def dokeepalive(self):
        if self.running:
            logger(0, "Doing Keepalive") #/
            r = http.client.HTTPConnection('127.0.0.1', local_port)
            body = body = pickle.dumps(getident())
            r.request("POST", "/keepalive", body=body)
            r.close()

    def start_running(self):
        self.running = True

    def stop_running(self):
        self.running = False

    def exit(self):
        self.stop_running()
        self.program_running = False

    def run(self):
        while self.program_running:
            while self.running:
                for i in range(30):
                    if self.running and self.program_running:
                        time.sleep(1)
                try:
                    self.dokeepalive()
                    self.timesfailed = 0
                except Exception as e:
                    if not isinstance(e, KeyboardInterrupt):
                        self.timesfailed += 1
                        logger(3, f"Keepalive Failed x{self.timesfailed}")

def logger(iloglevel, logmsg):
    loglevels = {0: "Debug", 1: "Info", 2: "Warn", 3: "Error", 4: "Fatal Error"}
    try:
        strloglevel = loglevels[iloglevel]
    except:
        strloglevel = loglevels[1]
    timelist = list(time.localtime())
    for i in [3,4,5]:
        if int(timelist[i]) < 10:
            timelist[i] = "0" + str(timelist[i]) 
    if iloglevel == 0 and dodebug or iloglevel != 0:
        print("[{0}/{1}/{2} {3}:{4}:{5}]".format(timelist[1],timelist[2],timelist[0],timelist[3],timelist[4],timelist[5]), end="")
        print(f"::{strloglevel}- ", end="")
        print(logmsg, flush=True)
    return 0
    
def getpubip():
    r = requests.get("https://api.ipify.org")
    return r.content

def getident():
    global ident
    global identcreated
    ip = getpubip()
    if ip == b"":
        raise Exception("Could not get public ip")
    if identcreated:
        mainident = ident[0]
        machineident = ident[1]
    else:
        sha = hashlib.sha256()
        sha.update(ip)
        mainident = sha.hexdigest()[:5]
        machineident = os.urandom(3).hex()
        identcreated = True
        ident = (mainident,machineident)
    return (mainident,machineident)

def identify():
    r = http.client.HTTPConnection('127.0.0.1', local_port)
    body = pickle.dumps(getident())
    r.request("POST", "/identify", body=body)
    retval = r.getresponse().read()
    r.close()
    retval = int(retval)
    return retval

def getnextjob():
    """
    Returns next Job object from server
    """
    logger(0, f"Getting New Job...")
    r = http.client.HTTPConnection('127.0.0.1', local_port)
    body = pickle.dumps(getident())
    r.request("POST", "/next", body=body)
    pjob = r.getresponse().read()
    r.close()
    if pjob != b"1":
        jlist = pickle.loads(pjob)
        j = job.Job(0, "DEPICKLE", "DEPICKLE")
        j.inputfromlist(jlist)
        return j
    else:
        return None

def returncompletejob(jobobj):
    logger(0, f"Returning Job: ID={jobobj.jobid}")
    r = http.client.HTTPConnection('127.0.0.1', local_port)
    jlist = jobobj.outputtolist()
    body = pickle.dumps([getident(),jlist])
    r.request("POST", "/return", body=body)
    retval = r.getresponse().read()
    r.close()
    retval = int(retval)
    return retval

def get_inprogress_job_by_id(jobid):
    pass #/

if __name__ == "__main__":
    multiprocessing.freeze_support()
    # Fix for Pyinstaller EXE

    # Print Botchgy Header
    header = [r" ____   ___ _____ ____ _   _  ______   __  ___ _   _  ____ ", r"| __ ) / _ \_   _/ ___| | | |/ ___\ \ / / |_ _| \ | |/ ___|", r"|  _ \| | | || || |   | |_| | |  _ \ V /   | ||  \| | |    ", r"| |_) | |_| || || |___|  _  | |_| | | |    | || |\  | |___ ", r"|____/ \___/ |_| \____|_| |_|\____| |_|   |___|_| \_|\____|"]
    for line in header:
        print(line)
    print()
    time.sleep(2)

    # Clean Exit Setup
    exitsig_obj = exitsig()
    signal.signal(signal.SIGINT, exitsig_obj.signal_handler)
    signal.signal(signal.SIGTERM, exitsig_obj.signal_handler)

    # SSH Tunnel Setup
    sshtunnel.DEFAULT_LOGLEVEL = logging.DEBUG #/
    try:
        tun = sshtunnel.SSHTunnelForwarder(hostip, 
                                        ssh_username=user,
                                        ssh_pkey= currentdir + "tkey.pem",
                                        remote_bind_address=("localhost", server_port),
                                        local_bind_address=("127.0.0.1", local_port),
                                        ssh_port=port)
        tun.start()
        exitsig_obj.addcleanupfxn(tun.stop)
    except sshtunnel.paramiko.ChannelException:
        exitsig_obj.signal_handler(0,0)
        sys.exit()

    # Send Ident to Server
    try:
        identify()
    except (ConnectionRefusedError, http.client.RemoteDisconnected) as e:
        logger(4,"Could not connect to server")
        exitsig_obj.signal_handler(0,0)

    # Keep Alive Thread Setup
    keepalive_obj = keepalive()
    keepalive_obj.start()
    keepalive_obj.start_running()
    exitsig_obj.addcleanupfxn(keepalive_obj.exit)

    # Make Multiprocessing Queue
    q = multiprocessing.Queue()

    # Exec Loop
    try:
        while True:
            # Check queue for responses
            try:
                jobexecreturn = q.get(block=False)
            except:
                #queue empty
                jobexecreturn = None

            
            if jobexecreturn != None:
                jobtoreturn = None
                #find job
                for j in inprogress_jobs:
                    if j.jobid == jobexecreturn[0]:
                        jobtoreturn = j

                #remove job from inprogress
                if jobtoreturn != None:
                    print("job to return is not none")
                    inprogress_jobs.remove(jobtoreturn) #/ not in list for some reason
                    #set data in job and set completedflag
                    logger(1, f"Completed Job: ID={jobtoreturn.jobid}")
                    jobtoreturn.data = jobexecreturn[1]
                    jobtoreturn.completedflag = True
                    completed_jobs.append(jobtoreturn)
                else:
                    print("job to return is none")

            if mp_availible_threads > 0 and completed_jobs == []:
                # Get and start new job
                next_job = getnextjob()
                if next_job != None:
                    logger(1, f"New Job Recieved: ID={next_job.jobid}")
                    logger(1, f"Starting Job: ID={next_job.jobid}")
                    #execute job
                    mp_availible_threads -= 1
                    inprogress_jobs.append(next_job)
                    proc = multiprocessing.Process(target=clientjobexec.executejob, args=(next_job.jobid,next_job.data[0],next_job.data[1],q))
                    proc.start()
                    logger(1, f"Jobs Running: {mp_max - mp_availible_threads}")

            if completed_jobs != []:
                #return job output
                jobstoremove = []
                for j in completed_jobs:
                    retval = returncompletejob(j)
                    if retval == 1:
                        raise Exception("Return Completed Job returned 1")
                    jobs_completed += 1
                    mp_availible_threads += 1
                    #output to logger
                    logger(1, f"Returned Job: ID={j.jobid}")
                    logger(1, f"Jobs Completed: {jobs_completed}")
                    #Add job to remove list
                    jobstoremove.append(j)

                for j in jobstoremove:
                    completed_jobs.remove(j)
    except KeyboardInterrupt:
        pass
    
    exitsig_obj.signal_handler(0,0)