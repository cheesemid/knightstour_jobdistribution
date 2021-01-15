#!/usr/bin/env python3

import multiprocessing as mp
import time
import sys

MAX_REC = 2000000

class jobexecclass:

    def __init__(self, id, startpointlist, movelist):
        self.id = id
        self.startpointlist = startpointlist
        self.movelist = movelist
        self.rcounter = 0
        pass

    def makearr(self,x, y):
        arr = []
        for i in range(y):
            currlist = []
            for j in range(x):
                currlist.append(0)
            arr.append(currlist)
        return arr

    def executejob(self, q):
        visited = self.makearr(8,8)
        starttime = time.time()
        try:
            self.ktour(self.startpointlist[1], self.startpointlist[0], 0, visited)
            print("Process Finished")
        except KeyboardInterrupt:
            print("---KeyboardInterrupt---")
            pass
        totaltime = time.time() - starttime
        q.put([self.rcounter,totaltime])
        sys.exit()


    def ktour(self,startx, starty, iteration, visited):
        self.rcounter += 1

        visited[starty][startx] = iteration

        if iteration == 64:
            return True

        if self.rcounter > MAX_REC:
            return False

        for move in self.movelist:
            testx = startx + move[1]
            testy = starty + move[0]

            if testx >= 0 and testx <= 7 and testy >= 0 and testy <= 7 and visited[testy][testx] == 0:

                if (self.ktour(testx,testy,iteration+1,visited)):
                    return True

        visited[starty][startx] = 0
        return False





def shuffle():
    for i in shufflelist:
        inputlist.append(originallist[i])

if __name__ == "__main__":
    mp.freeze_support()

    # P Vars
    originallist = [[-2,1],[-1,2],[1,2],[2,1],[1,-2],[2,-1],[-1,-2],[-2,-1]]
    inputlist = []

    ## VARS
    startpoint = [0,1]
    shufflelist = [7,0,1,2,3,4,5,6]

    shuffle()
    #executejob(startpoint,inputlist)

    proclist = []
    returnlist = []

    processcount = mp.cpu_count()-1 if mp.cpu_count() != 1 else 1
    q = mp.Queue()

    if mp.get_start_method() != "spawn":
        mp.set_start_method('spawn')
    print(mp.get_start_method())
    print(processcount)
    for i in range(processcount):
        k = jobexecclass(i+1, startpoint,inputlist)
        kprocess = mp.Process(target=k.executejob, args=(q,))
        proclist.append(kprocess)
        print("Spawning process: " + str(i+1))

    for p in proclist:
        p.start()
        print("Starting process: " + str(proclist.index(p)+1))

    getcounter = 0
    for p in proclist:
        ret = q.get() # will block
        getcounter += 1
        print(f"Getcounter {getcounter}")
        returnlist.append(ret)

    for p in proclist:
        p.join()



    while True:
        alldone = True
        for p in proclist:
            alldone = False if p.is_alive() else True
        if alldone:
            q.close()
            q.join_thread()
            avgrperslist = []
            maxs = -1
            totalr = 0
            for i in range(len(returnlist)):
                maxs = returnlist[i][1] if returnlist[i][1] > maxs else maxs
                totalr += returnlist[i][0]
                avgrperslist.append(returnlist[i][0]/returnlist[i][1])
            
            totrpers = totalr / maxs

            avgrpers = totalr/len(returnlist)
            avgrpers = avgrpers/maxs

            printformatting = "formatted" # formatted or raw
            if printformatting == "formatted":
                print("_____________________________")
                print(f"Rcounter: {totalr:,}")
                print(f"Total Time: {maxs:.2f}")
                print(f"Total R Per S Per Proc: {avgrpers:,.2f}")
                print(f"Total R Per S: {totrpers:,.2f}")
            elif printformatting == "raw":
                print("_____________________________")
                print(f"{totalr}")
                print(f"{maxs}")
                print(f"{avgrpers}")
                print(f"{totrpers}")
            break