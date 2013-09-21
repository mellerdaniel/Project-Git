'''
Created on Jun 22, 2013

@author: eitantorf
'''

from SeasonParser import SeasonParser
import time


class MeasuringTools(object):


    def __init__(self, pbpPath,singelGamePath,playersDataPath,testDataPath,trainDataPath):
        self.totalSuccessMeasures = 0
        self.totalFailMeasures = 0
        start = time.time()        
        
        #season = SeasonParser(pbpPath,singelGamePath,playersDataPath,testDataPath,trainDataPath,"regular",15)
        print('Measuring season: sliding window+ decision tree')
        season = SeasonParser(pbpPath,singelGamePath,playersDataPath,testDataPath,trainDataPath,"decisionTree",10)
        self.totalSuccessMeasures += season.gameParser.MeasuringStatistics[0]
        self.totalFailMeasures += season.gameParser.MeasuringStatistics[1]
        print("Total success :" + str(self.totalSuccessMeasures))
        print("Total fail :" + str(self.totalFailMeasures))
        totalGames = self.totalFailMeasures+ self.totalSuccessMeasures
        successPercentage = (float)((float)(self.totalSuccessMeasures)/(float)(totalGames))
        print("Total Percentage :" + str(successPercentage))
        end = time.time()
        
        print("Total running time for phase 0 : " +str(end - start))                
        
        '''
        print('Measuring season with last part only')
        season = SeasonParser(pbpPath,singelGamePath,playersDataPath,testDataPath,trainDataPath,"regular",10)
        self.totalSuccessMeasures += season.gameParser.MeasuringStatistics[0]
        self.totalFailMeasures += season.gameParser.MeasuringStatistics[1]
        print("Total success :" + str(self.totalSuccessMeasures))
        print("Total fail :" + str(self.totalFailMeasures))
        totalGames = self.totalFailMeasures+ self.totalSuccessMeasures
        successPercentage = (float)((float)(self.totalSuccessMeasures)/(float)(totalGames))
        print("Total Percentage :" + str(successPercentage))
        end = time.time()
        
        print("Total running time for phase 0 : " +str(end - start))                
        '''
        '''
        start = time.time()
        for i in range (7,40):
            print('Measuring with sliding window with {0} num of days'.format(abs(i)))
            season = SeasonParser(pbpPath,singelGamePath,playersDataPath,testDataPath,trainDataPath,"slidingWindow",i)
            print("Total success :" + str(season.totalSuccesfulMeasure))
            print("Total fail :" + str(season.totalFailMeasure))
            totalGames = season.totalFailMeasure + season.totalSuccesfulMeasure
            successPercentage = (float)((float)(season.totalSuccesfulMeasure)/(float)(totalGames))
            print("Total Percentage :" + str(successPercentage))
        end = time.time()
        print("Total running time for all sliding windows : " +str(end - start))
        '''