import re
import itertools
from GameParser import GameParser
from sets import Set
from pprint import pprint
from PlayersData import PlayersData
#constants
firstQuaterTime = "00:48:00"
firstTeamNamePlace = 8
secondTeamNamePlace = 11
teamNameSize = 3
EOF = ''



class SeasonParser:
    def __init__(self,pbpPath,singelGamePath,playersDataPath,testDataPath,trainDataPath,testSection):

        self.playByPlayDataPath = pbpPath
        self.singleGamePath = singelGamePath
        self.testGamePath = testDataPath
        self.trainGamePath = trainDataPath
        self.textFile = open(pbpPath,'r')
        self.textFile.close()
        self.textFile = open(pbpPath,'r')
        self.testSection = testSection
        self.totalSuccesfulMeasure = 0
        self.totalFailMeasure = 0
        #self.divideSeason(testSection)
#       self.playersData = PlayersData(playersDataPath)
        self.gameParser = GameParser(singelGamePath)
        if (testSection < 0):
            self.GAMES_WINDOW_NUMBER = abs(testSection)
            self.GAMES_MEASURE_NUMBER = 2   
            self.ParseSlidingWindow()
        else:
            self.parse()
            self.measure()
    #     self.FindCompleteRosters()
#         self.playersPermutations = {}
#         self.FindPermutations()
#         print("Finished Permutations 2")
#         self.CalcPermutations()
#         print("Finished Calculating 2")
#         self.FindPermutations(3)
#         print("Finished Permutations 3")
#         self.CalcPermutations()
#         print("Finished Calculating 3")
    def parse(self):
        #read entire play by play file
        pbpFile = open(self.trainGamePath,'r')
        pbpFile.close()
        pbpFile = open(self.trainGamePath,'r')
        pbpText = pbpFile.readlines() 
        i = 0
        rawData = pbpText[i]
        gameTime = rawData.split('\t')[2]
        while (gameTime==firstQuaterTime):
            i = i + 1
            rawData = pbpText[i]
            gameTime = rawData.split('\t')[2]
        #print(rawData)
        #print(pbpText[1446])
        while ((rawData != EOF)):
            teamAname = rawData[firstTeamNamePlace:firstTeamNamePlace+teamNameSize]
            teamBname = rawData[secondTeamNamePlace:secondTeamNamePlace+teamNameSize]
            self.gameParser.setTeamsName(teamAname, teamBname)
            
            #get game time in order to see if the current game is finished
            gameTime = rawData.split('\t')[2]
            gameFile = open(self.singleGamePath,'w')
            while (gameTime!=firstQuaterTime): 
                gameFile.write(rawData)
                i = i + 1
                
                if ((rawData != EOF) and (i < len(pbpText))):               
                    rawData = pbpText[i]
                    gameTime = rawData.split('\t')[2]
                else:
                    self.textFile.close()
                    gameFile.close()
                    self.gameParser.parseSingleGame()
                    #print("Finished parsing season")
                    #for team in self.gameParser.teamsRoster:
                    #    self.gameParser.printTeamData(team)
                    #exit()
                    rawData = EOF
                    break   
            #finished moving 1 game to a file, close the file and parse it.
            gameFile.close()   
            self.gameParser.parseSingleGame()
           
            #skip the not relavnt lines at the beginning of a match
            while (gameTime==firstQuaterTime):
                i = i + 1
                rawData = pbpText[i]
                gameTime = rawData.split('\t')[2]
    
    
    def ParseSlidingWindow(self):
        pbpFile = open(self.playByPlayDataPath,'r')
        pbpFile.close()
        pbpFile = open(self.playByPlayDataPath,'r')
        pbpText = pbpFile.readlines()
        dataGamesCounter = 0
        measureGamesCounter = 0 
        measureFlag = False
        i = 1
        rawData = pbpText[i]
        previousDateOfGames = rawData[:8]
        gameTime = rawData.split('\t')[2]
        teamsNumberOfGames = {}
        maximumDiffBetweenGames = 0
        while (gameTime==firstQuaterTime):
            i = i + 1
            rawData = pbpText[i]
            gameTime = rawData.split('\t')[2]
        #print(rawData)
        #print(pbpText[1446])
        while ((rawData != EOF)):
            
            teamAname = rawData[firstTeamNamePlace:firstTeamNamePlace+teamNameSize]
            teamBname = rawData[secondTeamNamePlace:secondTeamNamePlace+teamNameSize]
            if (teamAname in teamsNumberOfGames):
                teamsNumberOfGames[teamAname]+=1
            else:
                teamsNumberOfGames[teamAname] = 1
            if (teamBname in teamsNumberOfGames):
                teamsNumberOfGames[teamBname]+=1
            else:
                teamsNumberOfGames[teamBname] = 1
            self.gameParser.setTeamsName(teamAname, teamBname)           
            #get game time in order to see if the current game is finished
            gameDate = rawData[:8]
            if (gameDate != previousDateOfGames):
                if (measureFlag):
                    measureGamesCounter += 1
                    if (measureGamesCounter > self.GAMES_MEASURE_NUMBER):
                        measureGamesCounter = 0
                        measureFlag = False
                        self.totalSuccesfulMeasure += self.gameParser.MeasuringStatistics[0]
                        self.totalFailMeasure += self.gameParser.MeasuringStatistics[1]
                        self.gameParser = GameParser(self.singleGamePath)
                        self.gameParser.setTeamsName(teamAname, teamBname)
                        teamsNumberOfGames = {}
                else:
                    dataGamesCounter += 1
                    if (dataGamesCounter > self.GAMES_WINDOW_NUMBER):
                        dataGamesCounter = 0
                        measureFlag = True
                previousDateOfGames = gameDate
            gameTime = rawData.split('\t')[2]
            gameFile = open(self.singleGamePath,'w')
            while (gameTime!=firstQuaterTime): 
                gameFile.write(rawData)
                i = i + 1
                
                if ((rawData != EOF) and (i < len(pbpText))):               
                    rawData = pbpText[i]
                    gameTime = rawData.split('\t')[2]
                else:
                    self.textFile.close()
                    gameFile.close()
                    self.gameParser.parseSingleGame()
                    #print("Finished parsing season")
                    #for team in self.gameParser.teamsRoster:
                    #    self.gameParser.printTeamData(team)
                    #exit()
                    rawData = EOF
                    break   
            #finished moving 1 game to a file, now choosing - Parsing or measuring
            gameFile.close()   
            if (measureFlag):
                if (abs(teamsNumberOfGames[teamAname]- teamsNumberOfGames[teamBname]) > maximumDiffBetweenGames):
                    maximumDiffBetweenGames = abs(teamsNumberOfGames[teamAname]- teamsNumberOfGames[teamBname]) 
                self.gameParser.estimateSingleGame()
            else:
                self.gameParser.parseSingleGame()
            #skip the not relavnt lines at the beginning of a match
            while (gameTime==firstQuaterTime):
                i = i + 1
                rawData = pbpText[i]
                gameTime = rawData.split('\t')[2]
        print("Maximum number of games between teams - " + str(maximumDiffBetweenGames))        
    def FindCompleteRosters(self):
        self.fullLineups = {}
        for team in self.gameParser.teamsRoster:
            self.fullLineups[team] = []
            for roster in self.gameParser.teamsRoster[team]:
                for player in roster:
                    if not (player in self.fullLineups[team]):
                        self.fullLineups[team].append(player)
    def FindPermutations(self,numOfPlayers = 2):       
        for team in self.gameParser.teamsRoster:
            if not (team in self.playersPermutations):
                self.playersPermutations[team] = {}
            for players in list(itertools.permutations(self.fullLineups[team],numOfPlayers)):
                self.playersPermutations[team][frozenset(players)] = [0,0,0]
    def CalcPermutations(self):
        for team in self.gameParser.teamsRoster:
            for players in self.playersPermutations[team]:
                self.CalcTwoPlayersPreformance(players,team)
    
    def CalcTwoPlayersPreformance(self,players,team):
        for roster in self.gameParser.teamsRoster[team]:
            if (self.inRoster(roster,players)):
                self.playersPermutations[team][players][0]+= self.gameParser.teamsRoster[team][roster][0]
                self.playersPermutations[team][players][1]+= self.gameParser.teamsRoster[team][roster][1]
                self.playersPermutations[team][players][2]+= self.gameParser.teamsRoster[team][roster][2] 
    def inRoster(self,roster,players):
        for player in players:           
            if not (player in roster):
                return False
        return True   
    def divideSeason(self,testSection):
        #read entire play by play file
        pbpText = self.textFile.readlines()      
        i = 4
        rawData = pbpText[i]          
        #print(rawData)
        #print(pbpText[1446])
        counterTestGames = 0
        counterTrainGames = 0
        testFile = open(self.testGamePath,'w+')
        trainFile = open(self.trainGamePath,'w+')
        for i in range (1,4):
            if (testSection > 1):
                trainFile.write(pbpText[i])
            else:
                testFile.write(pbpText[i])
                
        counter = 0
        minLimit = (testSection - 1) * 123
        maxLimit = (testSection) * 123

        while ((rawData != EOF)):           
            #get game time in order to see if the current game is finished
            if ((counter >= minLimit) and (counter < maxLimit)):
                writeFile = testFile
                counterTestGames+= 1
            else:
                writeFile = trainFile
                counterTrainGames+=1 
            gameTime = rawData.split('\t')[2]
            while (gameTime!=firstQuaterTime): 
                writeFile.write(rawData)
                i = i + 1                
                if ((rawData != EOF) and (i < len(pbpText))):               
                    rawData = pbpText[i]
                    gameTime = rawData.split('\t')[2]
                else:
                    rawData = EOF
                    break   
            counter += 1
           
            #skip the not relavnt lines at the beginning of a match
            while (gameTime==firstQuaterTime):
                if ((counter >= minLimit) and (counter < maxLimit)):
                    writeFile = testFile
                else:
                    writeFile = trainFile
                writeFile.write(rawData)
                i = i + 1
                rawData = pbpText[i]
                gameTime = rawData.split('\t')[2]
                
        testFile.close()
        self.textFile.close()
        trainFile.close()
        #print('num of games for test are : {0}'.format(counterTestGames))
        #print('num of games for train are : {0}'.format(counterTrainGames))
    def measure(self):
        #read entire play by play file
        pbpFile = open(self.testGamePath,'r')
        pbpFile.close()
        pbpFile = open(self.testGamePath,'r')
        pbpText = pbpFile.readlines() 
        i = 0
        rawData = pbpText[i]
        gameTime = rawData.split('\t')[2]
        while (gameTime==firstQuaterTime):
            i = i + 1
            rawData = pbpText[i]
            gameTime = rawData.split('\t')[2]
        counterGames = 0
        #print(rawData)
        #print(pbpText[1446])
        while ((rawData != EOF)):
            teamAname = rawData[firstTeamNamePlace:firstTeamNamePlace+teamNameSize]
            teamBname = rawData[secondTeamNamePlace:secondTeamNamePlace+teamNameSize]
            self.gameParser.setTeamsName(teamAname, teamBname)
            
            #get game time in order to see if the current game is finished
            gameTime = rawData.split('\t')[2]
            gameFile = open(self.singleGamePath,'w')
            while (gameTime!=firstQuaterTime): 
                
                gameFile.write(rawData)
                i = i + 1
                
                if ((rawData != EOF) and (i < len(pbpText)-1)):               
                    rawData = pbpText[i]
                    gameTime = rawData.split('\t')[2]
                else:
                    self.textFile.close()
                    gameFile.close()
                    pbpFile.close()
                    self.gameParser.estimateSingleGame()
                    #print("Finished measuring season")
                    #print("number of total games are {0}".format(counterGames))
                    #self.gameParser.printStats()
                    rawData = EOF
                    return
            #finished moving 1 game to a file, close the file and parse it.
            gameFile.close()   
            self.gameParser.estimateSingleGame()
            counterGames+=1
            #skip the not relavnt lines at the beginning of a match
            while (gameTime==firstQuaterTime):
                i = i + 1
                rawData = pbpText[i]
                gameTime = rawData.split('\t')[2]