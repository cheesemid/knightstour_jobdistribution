#!/usr/bin/env python3

import time

class Job():

    def __init__(self, jobid, name, data, completedflag=False, execpy=None, callback=None, inittime=None, dispatchtime=None, expiretime=None):
        '''
            jobid => int id of job
            name => string name of job
            data => bstr pickled obj required to complete job
            completedflag => bool to specify if self.data is job input or job output
            execpy => bstr file contents of py to execute to setup or complete job
            callback => string callback information for contacting server when client finishes job
            inittime => int time when job was created at the server/backend (if None, will be initialized in __init__)
            dispatchtime => int time when job is given to the client (None for jobs not dispatched yet)
            expiretime => int time deadline for job (None if no deadline)
        '''
        self.jobid = jobid
        self.name = name
        self.data = data
        self.completedflag = completedflag
        self.execpy = execpy
        self.callback = callback
        if (inittime == None):
            self.inittime = int(time.time())
        else:
            self.inittime = inittime
        self.dispatchtime = dispatchtime
        self.expiretime = expiretime

    def outputtolist(self):
        return [self.jobid, self.name, self.data, self.completedflag, self.execpy, self.callback, self.inittime, self.dispatchtime, self.expiretime]

    def inputfromlist(self, inputlist):
        if len(inputlist) == 9:
            self.jobid, self.name, self.data, self.completedflag, self.execpy, self.callback, self.inittime, self.dispatchtime, self.expiretime = inputlist
        else:
            raise Exception("Inputlist must be of length 9")