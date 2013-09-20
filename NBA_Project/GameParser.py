'''
Created on Apr 10, 2013

@author: Daniel Meller
'''

import sys
import math
from sklearn import import tree
#constants
#import msvcrt as m
#def wait():
#    m.getch()
#global vars
EOF = ''
NUM_OF_LINEUP_PLAYERS = 5
teamNameSize = 3
NOT_A_PLAYER = "Team"
SUBSTITUTION = "Substitution"
TIMEOUT_OFFICALS = "Timeout: Official"
ERROR ="-1"
END_OF_QUARTER = "End of"
SECOND_QUARTER_TIME = "00:36:00"
THIRD_QUARTER_TIME = "00:24:00"
FOURTH_QUARTER_TIME = "00:12:00"
END_OF_GAME_TIME = "00:00:00"
SECOND_OVERTIME_TIME = "-00:05:00"
THIRD_OVERTIME_TIME = "-00:10:00"
FOURTH_OVERTIME_TIME = "-00:15:00"
POINTS_SIGN = "PTS"
FOURTH_QUARTER = "End of 4th Quarter"

class GameParser:
    currentStartMinutes = 48
    currentStartSeconds = 0
    teamAname = ""
    teamBname = ""
    teamsCurrentRoster = {}
    teamArosters = {}
    teamBrosters = {}
    teamsRoster = {}
    currentPoints = {}
    beforeSubCurrentPoints = {}
    currentEvaluatedPoints = {}
    MeasuringStatistics = [0,0]
    counter = 0
    pointsOffRealScore = 0
    
    #constructor - saves the path for the game file
    def __init__(self,filepath):
        self.fileName = filepath
        self.currentStartMinutes = 48
        self.currentStartSeconds = 0
        self.teamAname = ""
        self.teamBname = ""
        self.teamsCurrentRoster = {}
        self.teamArosters = {}
        self.teamBrosters = {}
        self.teamsRoster = {}
        self.teamsDataForTree = {}
        self.currentPoints = {}
        self.beforeSubCurrentPoints = {}
        self.currentEvaluatedPoints = {}
        self.MeasuringStatistics = [0,0]
        self.counter = 0
        self.pointsOffRealScore = 0
        self.decisionTrees = {}
        self.measureType = "regular"
    def parseSingleGame(self):
        
        '''
        Initializing parameters:
        GameTime = 48:00
        Finding starting lineup using the findStartingLineup method
        currentPoints for the current match        
        '''
        self.overTime = False
        self.currentStartMinutes = 48
        self.currentStartSeconds = 0
        self.currentGameFile = open(self.fileName,'r')
        self.gameText = self.currentGameFile.readlines()
        self.findStartingLineup(0)
        self.frozenRosters = {}
        self.currentPoints[self.teamAname] = 0
        self.currentPoints[self.teamBname] = 0
        self.beforeSubCurrentPoints[self.teamAname] = 0
        self.beforeSubCurrentPoints[self.teamBname] = 0
        self.frozenRosters[self.teamAname] = frozenset(self.teamsCurrentRoster[self.teamAname])
        self.frozenRosters[self.teamBname] = frozenset(self.teamsCurrentRoster[self.teamBname])
        
        #re read the game file
        #check if this teams didnt play already along the season
        if (not (self.teamAname in self.teamsRoster)):
            self.teamsRoster[self.teamAname]= {}
            self.teamsDataForTree[self.teamAname]= {}
        if (not (self.teamBname in self.teamsRoster)):
            self.teamsRoster[self.teamBname]= {}
            self.teamsDataForTree[self.teamBname]= {}
        
        #check if this rosters already played before, if not, initialize their score and time to 0
        if not (self.frozenRosters[self.teamAname] in self.teamsRoster[self.teamAname]):
            self.teamsRoster[self.teamAname][self.frozenRosters[self.teamAname]] = [0,0,0]
            self.teamsDataForTree[self.teamAname][self.frozenRosters[self.teamAname]] = {}
        if not (self.frozenRosters[self.teamBname] in self.teamsRoster[self.teamBname]):
            self.teamsRoster[self.teamBname][self.frozenRosters[self.teamBname]] = [0,0,0]
            self.teamsDataForTree[self.teamBname][self.frozenRosters[self.teamBname]] = {}
        
        #closing and opening in order to start reading the file from the beginning
        self.currentGameFile.close()
        self.currentGameFile = open(self.fileName,'r')
        self.gameText = self.currentGameFile.readlines()
        i = 0
        currentLine = self.gameText[i]
        gameTextLength = len(self.gameText)
        while ((i < gameTextLength) and (self.gameText[i] != EOF)) :
            #print(currentLine)
            #checking first if this a substitution line            
            if (self.substituteLine(currentLine)):
                currentTeam = self.getCurrentTeam(currentLine)
                #oppositeTeam = self.getOppositeTeam(currentTeam)
                self.teamsTimeUpdate(currentLine)               
                
                #this part is done for getting data for the decision tree
                self.calcRosterWinsWithFeatures()
                                     
                #usually subs comes together so additional checking for substitution are made
                #in order not to give "fake" rosters that didnt play together
                while (self.substituteLine(currentLine)):
                    if (self.endOfQuarterLine(i)):
                        self.findStartingLineup(i)
                        i = i+1
                        break
                    currentTeam = self.getCurrentTeam(currentLine)
                    subName = self.getSubName(currentLine)
                    currentPlayer = self.getCurrentPlayer(currentLine)
                    try:
                        self.teamsCurrentRoster[currentTeam].remove(currentPlayer)
                    except Exception:   
                        currentPlayer = 5
                    self.teamsCurrentRoster[currentTeam].add(subName)
                    i = i+1
                    currentLine = self.gameText[i]
                i=i-1
                #all subs done    
                self.frozenRostersDefine()
            else:
                #if not sub - checking end of quarter, in ends of quarter subs are being made
                # and a new roster has to be found
                if (self.endOfQuarterLine(i)):
                    
                    #if its end of 4th quarter it means that we have to sum up and check 
                    #for overtime
                    if (self.fourthQuarterLine(i)):                       
                        
                        #this is the check for overtime, if we still have lines to read, it means we have over time
                        if((i+1)<gameTextLength):
                            
                            self.teamsTimeUpdate(currentLine)
                            self.calcRosterWinsWithFeatures()
                            self.findStartingLineup(i+1)
                            self.frozenRostersDefine()
                            self.overTime = True
                            self.currentStartMinutes = 0
                            self.currentStartSeconds = 0
                        else:
                            #if not over time, just sum up the time rosters played
                            self.teamsTimeUpdate(currentLine)
                            self.calcRosterWinsWithFeatures()
                            break
                    else:
                        #sum up time, find new starting lineup for the next quarter
                        self.teamsTimeUpdate(currentLine)
                        self.calcRosterWinsWithFeatures()
                        self.findStartingLineup(i+1)
                        self.frozenRostersDefine()
                    
                    #self.debugPrint()
                    #raw_input("End of quarter, Press Enter to continue...")
                                                                  
                    
                else:
                    #if a basket were made in the current line, update teams status
                    if (self.pointsLine(currentLine)):
                        pointsFound = currentLine.find(POINTS_SIGN)
                        pointsFoundOvertime = 0
                        if (self.overTime):
                            pointsFoundOvertime = currentLine[currentLine.find('-')+1:].find('-') + 1
                    
                        #print(currentLine)
                        currentTeam = self.getCurrentTeam(currentLine)
                        oppositeTeam = self.getOppositeTeam(currentTeam)
                        pointsStart = currentLine.find("[")
                        pointsScored = currentLine[pointsStart+5:(pointsFound+pointsFoundOvertime)]
                        pointsMade = (int(pointsScored) - int(self.currentPoints[currentTeam]))
                        #points made by lineup
                        self.teamsRoster[currentTeam][self.frozenRosters[currentTeam]][1]+= pointsMade
                        #points against a lineup
                        self.teamsRoster[oppositeTeam][self.frozenRosters[oppositeTeam]][2]+= pointsMade
                        self.currentPoints[currentTeam]=pointsScored
                                          
            i = i + 1
            if (i!=gameTextLength):
                currentLine = self.gameText[i]
        #self.debugPrint()
        #raw_input("End of quarter, Press Enter to continue...")

        '''
        for team in self.teamsRoster:
            timeCounter = 0
            pointsCounter = 0
            print(team)
            for lineup in self.teamsRoster[team]:
                timeCounter+= self.teamsRoster[team][lineup][0]
                pointsCounter+= self.teamsRoster[team][lineup][1]
            print(team)
            print("Time:")
            print(timeCounter)
            print("Points:")
            print(pointsCounter)
        '''   
    def frozenRostersDefine(self):
        self.frozenRosters[self.teamAname] = frozenset(self.teamsCurrentRoster[self.teamAname])
        self.frozenRosters[self.teamBname] = frozenset(self.teamsCurrentRoster[self.teamBname])
                           
        if not ((self.frozenRosters[self.teamAname] in self.teamsRoster[self.teamAname])):
            self.teamsRoster[self.teamAname][self.frozenRosters[self.teamAname]]= [0,0,0]

        if not ((self.frozenRosters[self.teamBname] in self.teamsRoster[self.teamBname])):
            self.teamsRoster[self.teamBname][self.frozenRosters[self.teamBname]]= [0,0,0]
        
        #decision tree
        if not ((self.frozenRosters[self.teamAname] in self.teamsDataForTree[self.teamAname])):
            self.teamsDataForTree[self.teamAname][self.frozenRosters[self.teamAname]]= {}

        if not ((self.frozenRosters[self.teamBname] in self.teamsDataForTree[self.teamBname])):
            self.teamsDataForTree[self.teamBname][self.frozenRosters[self.teamBname]]= {}
                           
    def teamsTimeUpdate(self,currentLine):
        
        tempSeconds = self.currentStartSeconds
        tempMinutes = self.currentStartMinutes
        self.updateTimes(currentLine, self.teamAname)
        self.currentStartMinutes = tempMinutes
        self.currentStartSeconds = tempSeconds
        self.updateTimes(currentLine, self.teamBname)

        

    def updateTimes(self,currentLine,currentTeam):
        
        currentMinutes = self.getCurrentMinutes(currentLine)
        currentSeconds = self.getCurrentSeconds(currentLine)
        if (self.overTime == False):
            timeDiff =self.calculateTimeDiff(int(self.currentStartMinutes),int(self.currentStartSeconds),int(currentMinutes),int(currentSeconds))
        else:
            timeDiff =self.calculateTimeDiffOvertime(int(self.currentStartMinutes),int(self.currentStartSeconds),int(currentMinutes),int(currentSeconds))
        #if (timeDiff == 0):
            #print("WTF ITS 0")
            #print(currentLine)
                
        self.teamsRoster[currentTeam][self.frozenRosters[currentTeam]][0] += timeDiff
                    
        #update times
        self.currentStartMinutes = currentMinutes 
        self.currentStartSeconds = currentSeconds
                    
        
    def findStartingLineup(self,i):       
        if (i>= len(self.gameText)):
            return
        currentLine = self.gameText[i]
        gameTextLength = len(self.gameText)
        self.teamsCurrentRoster[self.teamAname] = set([])
        self.teamsCurrentRoster[self.teamBname] = set([])
        
        before_lineup_subs = {}
        before_lineup_subs[self.teamAname] = {}
        before_lineup_subs[self.teamBname] = {}
        #print(currentLine)
        while (i < gameTextLength):
            #team in row
            currentTeam = self.getCurrentTeam(currentLine)
            #player in action
            if (currentTeam != ERROR):
                currentPlayer = self.getCurrentPlayer(currentLine)           
                if ((currentPlayer != NOT_A_PLAYER) and (currentPlayer!=ERROR)):
                    if (currentLine.find(SUBSTITUTION) != -1):
        
                        subName = self.getSubName(currentLine)
                        #if not (currentPlayer in before_lineup_subs[currentTeam]):                            
                        before_lineup_subs[currentTeam][subName] = 1
                    #print(currentLine)
                    #print(currentTeam)
                    #print(before_lineup_subs)
                    #print(self.teamAname)
                    #print(self.teamBname)
                    #print(currentTeam)
                    if ((currentPlayer != NOT_A_PLAYER) and (not (currentPlayer in before_lineup_subs[currentTeam])) and ((currentLine.find(TIMEOUT_OFFICALS) == -1))):
                        if ((len(self.teamsCurrentRoster[currentTeam])) != NUM_OF_LINEUP_PLAYERS):
                            if not (currentPlayer in self.teamsCurrentRoster[currentTeam]):
                                self.teamsCurrentRoster[currentTeam].add(currentPlayer)                    
                    if ((len(self.teamsCurrentRoster[self.teamAname]) >= NUM_OF_LINEUP_PLAYERS) and (len(self.teamsCurrentRoster[self.teamBname]) == NUM_OF_LINEUP_PLAYERS)):
                        return                                   
            i = i + 1
            if (i!=gameTextLength):
                currentLine = self.gameText[i]
                
    def setTeamsName(self,teamA,teamB):
        self.teamAname = teamA
        self.teamBname = teamB
    def getCurrentPlayer(self,data):
        lineAb = data.find("LINE-AB")
        isTechnicalFoul = data.find(":Technical")
        if ((data.find("LINE-AUTO") != -1) or (lineAb != -1) or (isTechnicalFoul != -1)):
            return ERROR
        if (data.find("]") != -1):
            arr = data[data.find("]")+2:].split(' ')
            player = arr[0]
            if (player.find('.') != -1):
                player = player + arr[1]  
            return player 
        return ERROR
    
    def getCurrentMinutes(self,data):
        return (data.split(':')[1])
    def getCurrentSeconds(self,data):
        return (data.split(':')[2][:2])     
    def getCurrentTeam(self,data):
        if (data.find("[") != -1):
            startNameIndex = data.find("[")+1;
            return data[startNameIndex:startNameIndex+3]
        return ERROR
    def calculateTimeDiff(self,startMinutes,startSeconds,currentMinutes,currentSeconds):
        if (startSeconds < currentSeconds):
            return ((startMinutes-1- currentMinutes)*60+(startSeconds+60-currentSeconds))
        return ((startMinutes-currentMinutes)*60+(startSeconds-currentSeconds))
    def calculateTimeDiffOvertime(self,startMinutes,startSeconds,currentMinutes,currentSeconds):
        if (startSeconds > currentSeconds):
            return ((currentMinutes - 1 - startMinutes)*60+(currentSeconds+60-startSeconds))
        return ((currentMinutes-startMinutes)*60+(currentSeconds-startSeconds))
    def getOppositeTeam(self,team):
        if (team == self.teamAname):
            return self.teamBname
        return self.teamAname
    def getSubName(self,currentLine):
        arr = currentLine.split()
        if (arr[-2].find('.')!=-1):
            return arr[-2]+arr[-1]  
        return arr[-1]
    def substituteLine(self,currentLine):
        if (currentLine.find(SUBSTITUTION) != -1):
            return True
        else:
            return False
        
    def endOfQuarterLine(self,i):
        if (i == (len(self.gameText) - 1)):
            return True
        if ((self.gameText[i].find(SECOND_QUARTER_TIME) != -1) and (self.gameText[i+1].find(SECOND_QUARTER_TIME) == -1)): 
            return True
        if ((self.gameText[i].find(THIRD_QUARTER_TIME) != -1) and (self.gameText[i+1].find(THIRD_QUARTER_TIME) == -1)): 
            return True
        if ((self.gameText[i].find(FOURTH_QUARTER_TIME) != -1) and (self.gameText[i+1].find(FOURTH_QUARTER_TIME) == -1)): 
            return True
        if ((self.gameText[i].find(SECOND_OVERTIME_TIME) != -1) and (self.gameText[i+1].find(SECOND_OVERTIME_TIME) == -1)): 
            return True
        if ((self.gameText[i].find(THIRD_OVERTIME_TIME) != -1) and (self.gameText[i+1].find(THIRD_OVERTIME_TIME) == -1)): 
            return True
        if ((self.gameText[i].find(FOURTH_OVERTIME_TIME) != -1) and (self.gameText[i+1].find(FOURTH_OVERTIME_TIME) == -1)): 
            return True
        if ((self.gameText[i].find(END_OF_GAME_TIME) != -1) and (i == len(self.gameText))):
            return True
        if (i < len(self.gameText)-1):
            if ((self.gameText[i].find(END_OF_GAME_TIME) != -1) and ((self.gameText[i+1].find(END_OF_GAME_TIME) == -1))):
                return True 
        return False
    def fourthQuarterLine(self,i):
        if (self.gameText[i].find(END_OF_GAME_TIME) != -1):
            return True
        else:
            return False
    def pointsLine(self,currentLine):        
        pointsFound = currentLine.find(POINTS_SIGN)
        pointsFoundOverTime = 0
        if (self.overTime):
            pointsFoundOverTime = currentLine[currentLine.find('-')+1:].find('-')        
        teamSign = currentLine.find("]") 
        lineAuto = currentLine.find("LINE-AUTO")
        lineAb = currentLine.find("LINE-AB")
 
        if ((pointsFound != -1) and (lineAuto == -1) and (lineAb == -1) and ((pointsFoundOverTime+pointsFound) < teamSign)):
            if (self.overTime):
                    if (pointsFoundOverTime != -1):
                        return True
                    else:
                        return False 
            return True
        else:
            return False   
    #Debuging printing
    
    def printTeamData(self,team):               
        print(team)
        timeCounter = 0
        pointsCounter = 0
        for lineup in self.teamsRoster[team]:
            #print(lineup)
            timeCounter+= self.teamsRoster[team][lineup][0]
            pointsCounter+=self.teamsRoster[team][lineup][1]
        print("Time:")
        print(timeCounter)
        print("Points:")
        print(pointsCounter/82)
    
    def debugPrint(self):
        self.printTeamData(self.teamAname)
        self.printTeamData(self.teamBname)

    def buildDecisionTree(self):
        for team in self.teamsDataForTree:
            self.decisionTrees[team] = {}
            for roster in self.teamsDataForTree[team]:
                self.decisionTrees[team][roster] = tree.DecisionTreeClassifier()
                examples = []
                results = []
                for features in self.teamsDataForTree[team][roster]:
                    examples.append(features)
                    if (self.teamsDataForTree[team][roster][0] > 0):
                        results.append(1)
                    if (self.teamsDataForTree[team][roster][0] < 0):
                        results.append(0)
                self.decisionTrees[team][roster] = self.decisionTrees[team][roster].fit(examples,results)
    
    #MEASURE SINGLE GAME - should be here? maybe - for now it is.
    def estimateSingleGame(self):
        #self.counter += 1
        self.overTime = False
        self.currentStartMinutes = 48
        self.currentStartSeconds = 0
        self.currentGameFile = open(self.fileName,'r')
        self.gameText = self.currentGameFile.readlines()
        self.findStartingLineup(0)
        self.currentEvaluatedPoints[self.teamAname] = 0
        self.currentEvaluatedPoints[self.teamBname] = 0
        self.frozenRosters = {}
        self.frozenRosters[self.teamAname] = frozenset(self.teamsCurrentRoster[self.teamAname])
        self.frozenRosters[self.teamBname] = frozenset(self.teamsCurrentRoster[self.teamBname])
        
        self.currentGameFile.close()
        self.currentGameFile = open(self.fileName,'r')
        self.gameText = self.currentGameFile.readlines()
        i = 0
        try:
            currentLine = self.gameText[i]
        except:
            a = 5        
        gameTextLength = len(self.gameText)
        #if (currentLine.find('20080416UTASAS') != -1):
            #x=6
        self.calculateTeamsScore()
        while ((i < gameTextLength) and (self.gameText[i] != EOF)) :
            #print(currentLine)
            if (self.substituteLine(currentLine)):
                currentTeam = self.getCurrentTeam(currentLine)
                
                self.evaluateScore(currentLine)
                #usually subs comes together so additional checking for substitution are made
                #in order not to give "fake" rosters that didnt play together
                while (self.substituteLine(currentLine)):
                    if (self.endOfQuarterLine(i)):
                        self.findStartingLineup(i)
                        i = i+1
                        break
                    currentTeam = self.getCurrentTeam(currentLine)
                    subName = self.getSubName(currentLine)
                    currentPlayer = self.getCurrentPlayer(currentLine)
                    try:
                        self.teamsCurrentRoster[currentTeam].remove(currentPlayer)
                    except Exception:
                        a = 5
                    self.teamsCurrentRoster[currentTeam].add(subName)
                    i = i+1
                    currentLine = self.gameText[i]
                i=i-1
                #all subs done    
                self.frozenRostersDefine()
            else:
                #if not sub - checking end of quarter, in ends of quarter subs are being made
                # and a new roster has to be found
                if (self.endOfQuarterLine(i)):
                    
                    #if its end of 4th quarter it means that we have to sum up and check 
                    #for overtime
                    if (self.fourthQuarterLine(i)):                       
                        
                        #this is the check for overtime, if we still have lines to read, it means we have over time
                        if((i+5)<gameTextLength):
                            
                            self.evaluateScore(currentLine)
                            self.findStartingLineup(i+1)
                            self.frozenRostersDefine()
                            self.overTime = True
                            self.currentStartMinutes = 0
                            self.currentStartSeconds = 0
                        else:
                            #if not over time, just sum up the time rosters played
                    
                            break
                    else:
                        #sum up time, find new starting lineup for the next quarter
                        self.evaluateScore(currentLine)
                        self.findStartingLineup(i+1)
                        self.frozenRostersDefine()
                    
                    #self.debugPrint()
                    #raw_input("End of quarter, Press Enter to continue...")
                    
            i = i + 1        
            if (i < gameTextLength):
                currentLine = self.gameText[i]
        self.evaluateScore(currentLine)
        self.checkEvaluation(i-1)
        
    def estimateWithSingleGame(self):
        #self.counter += 1
        self.overTime = False
        self.currentStartMinutes = 48
        self.currentStartSeconds = 0
        self.currentGameFile = open(self.fileName,'r')
        self.gameText = self.currentGameFile.readlines()
        self.findStartingLineup(0)
        self.currentEvaluatedPoints[self.teamAname] = 0
        self.currentEvaluatedPoints[self.teamBname] = 0
        self.frozenRosters = {}
        self.frozenRosters[self.teamAname] = frozenset(self.teamsCurrentRoster[self.teamAname])
        self.frozenRosters[self.teamBname] = frozenset(self.teamsCurrentRoster[self.teamBname])
        
        self.currentGameFile.close()
        self.currentGameFile = open(self.fileName,'r')
        self.gameText = self.currentGameFile.readlines()
        i = 0
        try:
            currentLine = self.gameText[i]
        except:
            a = 5        
        gameTextLength = len(self.gameText)
        #if (currentLine.find('20080416UTASAS') != -1):
            #x=6
        self.calculateTeamsScore()
        while ((i < gameTextLength) and (self.gameText[i] != EOF)) :
            #print(currentLine)
            if (self.substituteLine(currentLine)):
                currentTeam = self.getCurrentTeam(currentLine)
                self.evaluateScore(currentLine)
                #usually subs comes together so additional checking for substitution are made
                #in order not to give "fake" rosters that didnt play together
                while (self.substituteLine(currentLine)):
                    if (self.endOfQuarterLine(i)):
                        self.findStartingLineup(i)
                        i = i+1
                        break
                    currentTeam = self.getCurrentTeam(currentLine)
                    subName = self.getSubName(currentLine)
                    currentPlayer = self.getCurrentPlayer(currentLine)
                    try:
                        self.teamsCurrentRoster[currentTeam].remove(currentPlayer)
                    except Exception:
                        a = 5
                    self.teamsCurrentRoster[currentTeam].add(subName)
                    i = i+1
                    currentLine = self.gameText[i]
                i=i-1
                #all subs done    
                self.frozenRostersDefine()
            else:
                #if not sub - checking end of quarter, in ends of quarter subs are being made
                # and a new roster has to be found
                if (self.endOfQuarterLine(i)):
                    
                    #if its end of 4th quarter it means that we have to sum up and check 
                    #for overtime
                    if (self.fourthQuarterLine(i)):                       
                        
                        #this is the check for overtime, if we still have lines to read, it means we have over time
                        if((i+5)<gameTextLength):
                            
                            self.evaluateScore(currentLine)
                            self.findStartingLineup(i+1)
                            self.frozenRostersDefine()
                            self.overTime = True
                            self.currentStartMinutes = 0
                            self.currentStartSeconds = 0
                        else:
                            #if not over time, just sum up the time rosters played
                    
                            break
                    else:
                        #sum up time, find new starting lineup for the next quarter
                        self.evaluateScore(currentLine)
                        self.findStartingLineup(i+1)
                        self.frozenRostersDefine()
                    
                    #self.debugPrint()
                    #raw_input("End of quarter, Press Enter to continue...")
                    
            i = i + 1        
            if (i < gameTextLength):
                currentLine = self.gameText[i]
        self.evaluateScore(currentLine)
        self.checkEvaluation(i-1)    
    def evaluateScore(self, currentLine):            
        timePlayed = self.getTimeForCurrentLineup(currentLine)
        if (self.measureType == "decisionTree"):
            lineupPoints = self.teamsRoster[self.teamBname][self.frozenRosters[self.teamBname]][1]
            lineupTime = self.teamsRoster[self.teamBname][self.frozenRosters[self.teamBname]][0]            
            opponentAveragePoints = ((float(lineupPoints) )/lineupTime)  
            opponnentHeight = self.getAverageHeight(self.frozenRosters[self.teamBname])
            opponnentWeight = self.getAverageWeight(self.frozenRosters[self.teamBname])
            opponenntFeatures = frozenset([opponnentHeight,opponnentWeight,opponentAveragePoints])
                        
            teamApointsMadeUntilSub = self.currentPoints[self.teamAname] - self.beforeSubCurrentPoints[self.teamAname]
            teamBpointsMadeUntilSub = self.currentPoints[self.teamBname] - self.beforeSubCurrentPoints[self.teamBname]            
            
            predictionResult = self.decisionTrees[self.teamAname][self.frozenRosters[self.teamAname]].predict(opponenntFeatures)
            #1 - teamA won , -1 = teamB won
            if (teamApointsMadeUntilSub != teamBpointsMadeUntilSub):
                result = ((teamApointsMadeUntilSub-teamBpointsMadeUntilSub)/(abs((teamApointsMadeUntilSub-teamBpointsMadeUntilSub))))
                if (predictionResult[0] == result):
                    self.MeasuringStatistics[0] += 1
                else:
                    self.MeasuringStatistics[1] += 1                         
            self.beforeSubCurrentPoints[self.teamAname] = self.currentPoints[self.teamAname]
            self.beforeSubCurrentPoints[self.teamBname] = self.currentPoints[self.teamBname]
            
        if (self.frozenRosters[self.teamAname] in self.teamsRoster[self.teamAname]):
            lineupPoints = self.teamsRoster[self.teamAname][self.frozenRosters[self.teamAname]][1]
            lineupOponentsPoints = self.teamsRoster[self.teamAname][self.frozenRosters[self.teamAname]][2]
            lineupTime = self.teamsRoster[self.teamAname][self.frozenRosters[self.teamAname]][0]
            if (lineupTime  == 0):
                self.currentEvaluatedPoints[self.teamAname] += self.teamAscore * timePlayed
            else:
                self.currentEvaluatedPoints[self.teamAname]  += ((float(lineupPoints) )/lineupTime) * timePlayed
        else:
            self.currentEvaluatedPoints[self.teamAname] += self.teamAscore * timePlayed
        if (self.frozenRosters[self.teamBname] in self.teamsRoster[self.teamBname]):
            lineupPoints = self.teamsRoster[self.teamBname][self.frozenRosters[self.teamBname]][1]
            lineupOponentsPoints = self.teamsRoster[self.teamBname][self.frozenRosters[self.teamBname]][2]
            lineupTime = self.teamsRoster[self.teamBname][self.frozenRosters[self.teamBname]][0]
            if (lineupTime == 0):
                self.currentEvaluatedPoints[self.teamBname] += self.teamBscore * timePlayed
            else:
                self.currentEvaluatedPoints[self.teamBname]  += ((float(lineupPoints) )/lineupTime) * timePlayed
        else:
            self.currentEvaluatedPoints[self.teamBname]  += self.teamBscore * timePlayed
            
    def checkEvaluation(self, i):
        while (self.gameText[i].find(POINTS_SIGN) == -1):
            i = i-1
        currentLine = self.gameText[i]
        currentTeam = self.getCurrentTeam(currentLine)

        currentOponentTeam = self.getOppositeTeam(currentTeam)
        if (self.overTime):
            currentLine = currentLine.replace("-", "x", 1)
        realScore = {}
        realScore[currentTeam] = currentLine[currentLine.find("[")+5:currentLine.find("-")]
        realScore[currentOponentTeam] = currentLine[currentLine.find("-") + 1:currentLine.find("]")]
        winningTeam = self.teamAname if (int(realScore[self.teamAname]) > int(realScore[self.teamBname])) else self.teamBname
        evaluateWinningTeam = self.teamAname if (self.currentEvaluatedPoints[self.teamAname] > self.currentEvaluatedPoints[self.teamBname]) else self.teamBname
        self.pointsOffRealScore += math.fabs(int(self.currentEvaluatedPoints[self.teamAname])-int(realScore[self.teamAname]))
        self.pointsOffRealScore += math.fabs(int(self.currentEvaluatedPoints[self.teamBname])-int(realScore[self.teamBname]))
        if (winningTeam == evaluateWinningTeam):
            self.MeasuringStatistics[0] += 1
        else:
            self.MeasuringStatistics[1] += 1
        #except Exception, e:
        #    print "Couldn't do it: %s" % e
        #    a = 5

    def getTimeForCurrentLineup(self,currentLine):
        currentMinutes = self.getCurrentMinutes(currentLine)
        currentSeconds = self.getCurrentSeconds(currentLine)
        if (self.overTime == False):
            timeDiff =self.calculateTimeDiff(int(self.currentStartMinutes),int(self.currentStartSeconds),int(currentMinutes),int(currentSeconds))
        else:
            timeDiff = self.calculateTimeDiffOvertime(int(self.currentStartMinutes),int(self.currentStartSeconds),int(currentMinutes),int(currentSeconds))
        
                    
        #update times
        self.currentStartMinutes = currentMinutes 
        self.currentStartSeconds = currentSeconds
        
        return timeDiff
    def printStats(self):
        #print(self.counter)
        #print(float(self.pointsOffRealScore)/self.counter)
        print("Evaluation succeeded " + (str)(self.MeasuringStatistics[0]) + " times" )
        print("Evaluation failed " + (str)(self.MeasuringStatistics[1]) + " times" )
    def calculateTeamsScore(self):
        # calculate a global score for the team
        timeCounter = 0 
        pointsCounter = 0 
        oponenetPointsCounter = 0
        for lineup in self.teamsRoster[self.teamAname]:
            timeCounter+= self.teamsRoster[self.teamAname][lineup][0]
            pointsCounter+=self.teamsRoster[self.teamAname][lineup][1]
            oponenetPointsCounter+=self.teamsRoster[self.teamAname][lineup][2]
        self.teamAscore = (float(oponenetPointsCounter))/timeCounter
            
        timeCounter = 0 
        pointsCounter = 0 
        oponenetPointsCounter = 0
        for lineup in self.teamsRoster[self.teamBname]:
            timeCounter+= self.teamsRoster[self.teamBname][lineup][0]
            pointsCounter+=self.teamsRoster[self.teamBname][lineup][1]
            oponenetPointsCounter+=self.teamsRoster[self.teamBname][lineup][2]
        self.teamBscore = (float(oponenetPointsCounter))/timeCounter
    
    
    def calcRosterWinsWithFeatures(self):
        
        if ((self.teamsRoster[self.teamAname][self.frozenRosters[self.teamAname]][0]==0)) or ((self.teamsRoster[self.teamBname][self.frozenRosters[self.teamBname]][0] == 0)):
            return            
        teamApointsNormalized = (float(self.teamsRoster[self.teamAname][self.frozenRosters[self.teamAname]][1])/(self.teamsRoster[self.teamAname][self.frozenRosters[self.teamAname]][0]))
        teamBpointsNormalized = (float(self.teamsRoster[self.teamBname][self.frozenRosters[self.teamBname]][1])/(self.teamsRoster[self.teamBname][self.frozenRosters[self.teamBname]][0]))
        teamAHeightWeightPoints = frozenset([self.getAverageHeight(self.frozenRosters[self.teamAname]),self.getAverageWeight(self.frozenRosters[self.teamAname]),teamApointsNormalized])
        teamBHeightWeightPoints = frozenset([self.getAverageHeight(self.frozenRosters[self.teamBname]),self.getAverageWeight(self.frozenRosters[self.teamBname]),teamBpointsNormalized])
        
        if not (teamAHeightWeightPoints in self.teamsDataForTree[self.teamAname][self.frozenRosters[self.teamAname]]):
            self.teamsDataForTree[self.teamAname][self.frozenRosters[self.teamAname]][teamAHeightWeightPoints] = [0,0,0]
        if not (teamBHeightWeightPoints in self.teamsDataForTree[self.teamBname][self.frozenRosters[self.teamBname]]):
            self.teamsDataForTree[self.teamBname][self.frozenRosters[self.teamBname]][teamBHeightWeightPoints] = [0,0,0]
        
        #were saving the following data
        #teamsDataForTree[0] - wins over such type of roster
        #teamsDataForTree[1] - points made over such roster
        #teamsDataForTree[2] - points scored on the roster
        teamApointsMadeUntilSub = self.currentPoints[self.teamAname] - self.beforeSubCurrentPoints[self.teamAname]
        teamBpointsMadeUntilSub = self.currentPoints[self.teamBname] - self.beforeSubCurrentPoints[self.teamBname]
        
        if ((teamApointsMadeUntilSub - teamBpointsMadeUntilSub)>0):
            self.teamsDataForTree[self.teamAname][self.frozenRosters[self.teamAname]][teamAHeightWeightPoints][0]+= 1                    
            self.teamsDataForTree[self.teamAname][self.frozenRosters[self.teamBname]][teamAHeightWeightPoints][0]-= 1
        if ((teamApointsMadeUntilSub - teamBpointsMadeUntilSub)<0):
            self.teamsDataForTree[self.teamAname][self.frozenRosters[self.teamAname]][teamAHeightWeightPoints][0]-= 1                    
            self.teamsDataForTree[self.teamAname][self.frozenRosters[self.teamBname]][teamAHeightWeightPoints][0]+= 1
        
        self.teamsDataForTree[self.teamAname][self.frozenRosters[self.teamAname]][teamAHeightWeightPoints][1]+= teamApointsMadeUntilSub
        self.teamsDataForTree[self.teamAname][self.frozenRosters[self.teamAname]][teamAHeightWeightPoints][2]+= teamBpointsMadeUntilSub
        self.teamsDataForTree[self.teamBname][self.frozenRosters[self.teamBname]][teamBHeightWeightPoints][1]+= teamBpointsMadeUntilSub
        self.teamsDataForTree[self.teamBname][self.frozenRosters[self.teamBname]][teamBHeightWeightPoints][2]+= teamApointsMadeUntilSub
            
        self.beforeSubCurrentPoints[self.teamAname] = self.currentPoints[self.teamAname]
        self.beforeSubCurrentPoints[self.teamBname] = self.currentPoints[self.teamBname]
            
    def getAverageWeight(self,frozenRoster):
        return 1
    def getAverageHeight(self,frozenRoster):
        return 1  