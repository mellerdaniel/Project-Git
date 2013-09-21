'''
Created on Apr 10, 2013

@author: Daniel Meller
'''
from MeasuringTools import MeasuringTools
#constants
firstQuaterTime = "00:48:00"
#playByPlayPath = '/Users/eitantorf/Documents/Eclipse Workspace/NBA/Play by play data/playbyplay20072008reg.txt'
#playByPlayPath = r'C:\Users\User\Dropbox\NBA\Play by play data\playbyplay20072008reg20081211.txt'
playByPlayPath = r'/home/mellerdaniel/Dropbox/NBA/Play by play data/playbyplay20072008reg20081211.txt'


#playersInfoPath = r'C:\Users\User\Dropbox\NBA\Play by play data\playersInfo.txt'
playersInfoPath = r'/home/mellerdaniel/Dropbox/NBA/Play by play data/playersInfo.txt'

#singleGamePath = '/Users/eitantorf/Documents/Eclipse Workspace/NBA/Play by play data/gameFile.txt'
#singleGamePath = r'C:\Users\User\Dropbox\NBA\Play by play data\gameFile.txt'
singleGamePath = r'/home/mellerdaniel/Dropbox/NBA/Play by play data/gameFile.txt'



#testDataPath = '/Users/eitantorf/Documents/Eclipse Workspace/NBA/Play by play data/testFile.txt'
#testDataPath = r'C:\Users\User\Dropbox\NBA\Play by play data\testFile.txt'
testDataPath = r'/home/mellerdaniel/Dropbox/NBA/Play by play data/testFile.txt'

#trainDataPath = r'C:\Users\User\Dropbox\NBA\Play by play data\trainFile.txt'
#trainDataPath = '/Users/eitantorf/Documents/Eclipse Workspace/NBA/Play by play data/trainFile.txt'
trainDataPath = r'/home/mellerdaniel/Dropbox/NBA/Play by play data/trainFile.txt'

firstTeamNamePlace = 8
secondTeamNamePlace = 11
teamNameSize = 3
EOF = ''


#Creating an instance of game parser
#gameParser = GameParser(singleGamePath_Meller)

#measuringTools = MeasuringTools(playByPlayPath_Eitan,singleGamePath_Eitan,playersInfoPath_Eitan,testDataPath_Eitan,trainDataPath_Eitan)
measuringTools = MeasuringTools(playByPlayPath,singleGamePath,playersInfoPath,testDataPath,trainDataPath)

#Checking how the maximum amount of games two different between two teams matching
#debug print test for players positions

#for team in playersData.players:
#    for player in playersData.players[team]:
#        #print(playersData.players[team][player][0] + ' ' + player )
#        print(playersData.players[team][player][0] + ' ' + player + ' ' + playersData.players[team][player][1])

