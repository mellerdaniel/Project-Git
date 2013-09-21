'''

Created on Sep 7, 2013



@author: eitantorf

'''

import re

import itertools

from sets import Set

from pprint import pprint

EOF = ''

class PlayerFeatures:
    
    def __init__(self,dataPath):
        self.dataPath = dataPath
        self.buildPlayersFeatures()

    def buildPlayersFeatures(self):
        self.playersByTeams = {}
        dataFile = open(self.dataPath,'r')
        dataFile.close()
        dataFile = open(self.dataPath,'r')
        dataLines = dataFile.readlines() 
        i = 0
        for line in dataLines:

            rawData = dataLines[i]

            if rawData.startswith('['):
                currentTeam = rawData[1:4]
                self.playersByTeams[currentTeam] = {}
            else:
                firstName =  rawData[rawData.find(',') + 1 : rawData.find(' ')]
                rawData = rawData[rawData.find(',') + 1 : len(rawData) - 1]
                lastName = rawData[rawData.find(' ') + 1 : rawData.find(',')]
                rawData = rawData[rawData.find(',') + 1 : len(rawData) - 1]
                rawData = rawData[rawData.find(',') + 1 : len(rawData) - 1]
                height =  rawData[0 : rawData.find(',')]
                heightInInches = int(float(height[0])) * 12 + int(float(height[2 : len(height)]))
                rawData = rawData[rawData.find(',') + 1 : len(rawData) - 1]
                weight = rawData[0 : rawData.find(',')]

                if  not (lastName in self.playersByTeams[currentTeam]):
                    self.playersByTeams[currentTeam][lastName] = {}
                self.playersByTeams[currentTeam][lastName][firstName] =  [self.inchToCM(heightInInches), int(float(weight))]
                
            i = i + 1


    def inchToCM(self, feet):
        return feet * 2.54

    

    def calculateLineupFeatures(self, team, lineup):
        weightSum = 0
        heightSum = 0
        for player in lineup:
            if (player.find('.') != -1):
                partialFistName = player[0 : player.find('.')]
                try:
                    lastName = player[player.find('.') + 1 : len(player)]
                    count = 0
                    for k, v in self.playersByTeams[team][lastName].iteritems():
                        if k.startswith(partialFistName):
                            count += 1
                            heightSum += self.playersByTeams[team][lastName][k][0]
                            weightSum += self.playersByTeams[team][lastName][k][1]
                    if (count >= 2):
                        print(team)
                except Exception as e: 
                    print(e)
            else:
                heightSum += self.playersByTeams[team][player].itervalues().next()[0]
                weightSum += self.playersByTeams[team][player].itervalues().next()[1]
        return [heightSum/5, weightSum/5]

            

                

            

