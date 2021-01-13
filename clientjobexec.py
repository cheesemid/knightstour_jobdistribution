#!/usr/bin/env python3

rcounter = 0
movelist = []

def makearr(x, y):
        arr = []
        for i in range(y):
            currlist = []
            for j in range(x):
                currlist.append(0)
            arr.append(currlist)
        return arr

def executejob(startpointlist, inputmovelist):
    global rcounter
    global movelist
    movelist = inputmovelist
    rcounter = 0
    visited = makearr(8,8)
    if ktour(startpointlist[1], startpointlist[0], 0, visited):
        return rcounter
    return -1


def ktour(startx, starty, iteration, visited):
        global rcounter
        global movelist
        rcounter += 1

        visited[starty][startx] = iteration
        if rcounter > 600000: #/
            return True

        if iteration == 64:
            return True

        for move in movelist:
            testx = startx + move[1]
            testy = starty + move[0]

            if testx >= 0 and testx <= 7 and testy >= 0 and testy <= 7 and visited[testy][testx] == 0:

                if (ktour(testx,testy,iteration+1,visited)):
                    return True

        visited[starty][startx] = 0
        return False