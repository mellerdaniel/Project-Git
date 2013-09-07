'''
Created on May 19, 2013

@author: User
'''
EOF = ''
TEAM = 4
PLAYER = 1
POSITION = 2
NOT_LEGAL = 'Rk'
FIRST_NAME = "FirstName"

class PlayersData(object):
    '''
    classdocs
    '''
    def __init__(self,filepath):
        self.textFile = open(filepath,'r')
        self.players = {}
        self.ParseData()
        '''
        Constructor
        '''
    def ParseData(self):
        playersFile = self.textFile.readlines()
        i = 0
        data = playersFile[i]
        while ((data != EOF) and (i < len(playersFile))):
            splitData = data.split(',')
            if (self.isLegal(splitData[0])):
                team = splitData[TEAM]
                names = splitData[PLAYER].split(' ')
                playerFirstName = names[0]
                playerLastName = names[1]               
                position = splitData[POSITION]
                if team in self.players:
                    self.players[team][playerLastName] = [playerFirstName,position]
                else:
                    self.players[team] = {}
                    self.players[team][playerLastName] = [playerFirstName,position]
            i= i+1
            if (i < len(playersFile)):
                data = playersFile[i]
            
    def isLegal(self,data):
        if (data == NOT_LEGAL):
            return False
        return True
    
        
        
            