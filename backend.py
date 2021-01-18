#!/usr/bin/env python3

import os
import job
import pickle
import time

import permutation

dodebug = True
joblist = []
activeclients = []

basepath = __file__
currentdir = ""
for i in range(len(basepath.split("/"))-1):
    currentdir = currentdir + basepath.split("/")[i] + "/"

class client():
    def __init__(self, ident, lastkeepalive=0, currentjob=[]):
        self.ident = ident
        if lastkeepalive == 0:
            self.lastkeepalive = int(time.time())
        else:
            self.lastkeepalive = lastkeepalive
        self.currentjob = currentjob

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

def initenv():
    global joblist
    try:
        os.mkdir(currentdir + "clientinfo")
    except FileExistsError:
        logger(1, "Clientinfo dir exists")

    try:
        os.mkdir(currentdir + "completedjobs")
    except FileExistsError:
        logger(1, "Completedjobs dir exists")

    ls = os.listdir(currentdir)
    if "server.py" not in ls:
        raise Exception("Server.py cannot be found")


    # initialize joblist
    if "pjoblist.bin" not in ls:
        logger(1, "Pjoblist.bin does not exist... Creating...")
        jobid = 0
        startpointlist = [[0,0],[0,1],[0,2],[0,3],[1,1],[1,2],[1,3],[2,2],[2,3],[3,3]]
        originalmovelist = [[-2,1],[-1,2],[1,2],[2,1],[1,-2],[2,-1],[-1,-2],[-2,-1]]
        for s in startpointlist:
            for p in permutation.permutation(list(range(8))):
                currmovelist = []
                for num in p:
                    currmovelist.append(originalmovelist[num])

                datalist = []
                datalist.append(s)
                datalist.append(currmovelist)

                currjob = job.Job(jobid, f"{s[0]}-{s[1]}.{p[0]}{p[1]}{p[2]}{p[3]}{p[4]}{p[5]}{p[6]}{p[7]}", datalist)
                joblist.append(currjob)
                jobid += 1

        outf = open(currentdir + "pjoblist.bin", "wb")
        joblistlist = [j.outputtolist() for j in joblist]
        pjoblistlist = pickle.dumps(joblistlist)
        outf.write(pjoblistlist)
        outf.close()
        logger(1,"Jobs Left: " + str(len(joblist)))
    else:
        logger(1, "Pjoblist.bin exists... Loading...")
        inf = open(currentdir + "pjoblist.bin", "rb")
        joblistlist = pickle.load(inf)
        for jlist in joblistlist:
            newjob = job.Job(0, "DEPICKLE", "DEPICKLE")
            newjob.inputfromlist(jlist)
            joblist.append(newjob)
        inf.close()
        logger(1,"Jobs Left: " + str(len(joblist)))

    return True

def getnextjob(data):
    # From /next
    """
    Server side code for /next page
    Client requests /next with pickled ident tuple to receive popped job from joblist
    Returns job if successful and b"1" if failed 
    """
    try:
        ident = pickle.loads(data)
    except:
        logger(2,"Failed getnext job: Data was None")
        return b"1"
    c = getclient(ident)
    if c != None:
        try:
            dispatch = joblist.pop()
        except IndexError:
            logger(2, "JOBLIST IS EMPTY")
        dispatch.dispatchtime = int(time.time())
        c.currentjob.append(dispatch)
        tosend = pickle.dumps(dispatch.outputtolist())
        logger(1,"Jobs Left: " + str(len(joblist)))
        return tosend
    else:
        logger(2,"Failed getnext job: Client not found")
    return b"1"
    

def returnjob(data):
    # From /return
    """
    Server side code for /return page
    Client requests /return with pickled ident tuple and job result data to return job
    Data (is pickled) -> [(mainident,machineident),job in list form]
    Makes file in completedjobs dir named {job.name}.txt
    Returns b"0" if successful and b"1" if failed 
    """
    try:
        qdata = pickle.loads(data)
    except:
        logger(2,"Failed returnjob: Data was None")
        return b"1"
    ident = qdata[0]
    completedjobaslist = qdata[1]
    completedjob = job.Job(0, "DEPICKLE", "DEPICKLE")
    completedjob.inputfromlist(completedjobaslist)
    if completedjob.completedflag == True:
        jobls = os.listdir(currentdir + "completedjobs")
        if str(completedjob.name + ".txt") not in jobls:
            outfjob = open(currentdir + "completedjobs/" + str(completedjob.name) + ".txt", "w")
            outfjob.write(str(completedjob.data))
            
            clientls = os.listdir(currentdir + "clientinfo")
            if str(str(ident[0]) + ".txt") in clientls:
                infclient = open(currentdir + "clientinfo/" + str(ident[0]) + ".txt", "r")
                numjobsdone = infclient.readline()
                totalrecursions = infclient.readline()
                totalseconds = infclient.readline()
                avgrpers = infclient.readline()
                numjobsdone.strip("\n")
                avgrpers.strip("\n")
                totalrecursions.strip("\n")
                totalseconds.strip("\n")
                numjobsdone = int(numjobsdone)
                avgrpers = int(avgrpers)
                totalrecursions = int(totalrecursions)
                totalseconds = int(totalseconds)
                infclient.close()
                outfclient = open(currentdir + "clientinfo/" + str(ident[0]) + ".txt", "w")
                outfclient.write(str(numjobsdone + 1) + "\n") #numjobsdone
                outfclient.write(str(totalrecursions + int(completedjob.data)) + "\n") #totalrecursions
                outfclient.write(str((totalseconds + (int(time.time()) - int(completedjob.dispatchtime)))) + "\n") #totalseconds
                outfclient.write(str(int((totalrecursions + int(completedjob.data))/(totalseconds + (int(time.time()) - int(completedjob.dispatchtime)+1)))) + "\n") #avgrpers
            else:
                outfclient = open(currentdir + "clientinfo/" + str(ident[0]) + ".txt", "w")
                outfclient.write(str(1) + "\n") #numjobsdone
                outfclient.write(str(completedjob.data) + "\n") #totalrecursions
                outfclient.write(str(completedjob.data) + "\n") #totalseconds
                outfclient.write(str(int(int(completedjob.data)/((int(time.time()) - int(completedjob.dispatchtime)+1)))) + "\n") #avgrpers

            c = getclient(ident)
            jobtoremove = None
            for j in c.currentjob:
                if j.jobid == completedjob.jobid:
                    jobtoremove = j
            if jobtoremove != None:
                logger(1,f"Job {jobtoremove.jobid} Completed by: {ident[0]}")
                c.currentjob.remove(j)
            else:
                raise Exception("Job not found")

            logger(1,"Jobs Left: " + str(len(joblist)))
            return b"0"
        else:
            #Completed Job Already Exists
            logger(0, "Completed Job Already Exists")
            return b"1"
    else:
        #Completed flag is not set to True
        logger(0, "Completed flag is not set to True")
        return b"1"

def addclient(data):
    # From /identify
    """
    Server side code for /identify page
    Client requests /identify with pickled ident tuple to be added to activeclients
    Returns b"0" if successful and b"1" if failed 
    """
    try:
        ident = pickle.loads(data)
    except:
        logger(2,"Failed getnext job: Data was None")
        return b"1"
    if len(ident[0]) == 5 and len(ident[1]) == 6:
        if getclient(ident) == None:
            activeclients.append(client(ident))
        else:
            logger(0, f"Client already active: {ident}")
        logger(0, f"Addclient: {ident}")
        return b"0"
    return b"1"

def removeclient(ident):
    toremove = None
    for c in activeclients:
        if c.ident == ident:
            toremove = c
    if toremove != None:
        activeclients.remove(toremove)
        return 0
    else:
        return 1

def getclient(ident):
    locatedclient = None
    for c in activeclients:
        if c.ident == ident:
            locatedclient = c
    return locatedclient

def updatekeepalive(data):
    # From /keepalive
    """
    Server side code for /keepalive page
    Client requests /keepalive with pickled ident tuple to updatekeepalive counter
    Returns b"0" if successful and b"1" if failed    
    """
    try:
        ident = pickle.loads(data)
    except:
        logger(2,"Failed updatekeepalive job: Data was None")
        return b"1"
    c = getclient(ident)
    if c != None:
        c.lastkeepalive = int(time.time())
        checkkeepalive()
        return b"0"
    checkkeepalive()
    return b"1"

def checkkeepalive():
    """
    Checks all clients in active clients for overdue keepalive timers
    Appends all jobs from removed clients to joblist
    Limit is 180s
    """
    logger(0,"Checking Keepalives")
    toremove = []
    for c in activeclients:
        if int(time.time()) - c.lastkeepalive > 180:
            toremove.append(c)
    logger(0,f"Toremove = {toremove}")
    for c in toremove:
        if c.currentjob != []:
            for j in c.currentjob:
                joblist.append(j)
                logger(0,f"Recycling Job: ID={j.jobid}")
        activeclients.remove(c)

def admin(data):
    # From /admin
    """
    Server side code for /admin page
    Admin requests /admin with list containing pickled admin ident and optional command
    Returns output dict without command or b"0" with command if successful and b"1" if failed    
    """
    correctadminident = "5a4544"
    try:
        inlist = pickle.loads(data)
    except:
        logger(2,"Failed admin job: Data was None")
        return b"1"
    if inlist[0] != correctadminident:
        logger(2,"Failed admin job: Auth was incorrect")
        return b"1"
    elif inlist[0] == correctadminident:
        #authenticated
        if len(inlist) > 1:
            command = inlist[1]
        else:
            command = ""
        logger(1, f"Admin logged in: Running command \"{command}\"")
        if command == "":
            output = {"numclientsconnected": len(activeclients), "clientsconnected": [c.ident[0] for c in activeclients],"jobsleft": len(joblist)}
            return pickle.dumps(output)
        #add functionality for commands
    return b"Hello Sir"

def shutdown():
    # Saves all job data
    for c in activeclients:
        if c.currentjob != []:
            for j in c.currentjob:
                joblist.append(j)
    outf = open(currentdir + "pjoblist.bin", "wb")
    joblistlist = [j.outputtolist() for j in joblist]
    pjoblistlist = pickle.dumps(joblistlist)
    logger(1, "Writing Joblist to file")
    outf.write(pjoblistlist)
    outf.close()
    return 0

if __name__ == "__main__":
    initenv()
