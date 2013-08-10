'''
Created on May 25, 2013

@author: User
'''
PG = 'PG' # Point Guard
SG = 'SG' # Shooting Guard 
CENTER = 'C' # Center
PF = 'PF' # Power forward
SF = 'SF' # Small forward
NO_PLAYER_IN_POSITION = "-1"
from SeasonParser import SeasonParser
class Measure:
    
    def __init__(self,seasonData):
        self.data = seasonData
    
    def GradeRosterByPositions(self,team,roster,positions,percentage):
        [posPlayers, restPlayers] = self.GetPlayersByPosition(roster,positions)
    
    def GetPlayersByPosition(self,team,roster,positions):
        for position in positions:
            
    '''def GetSinglePlayerByPosition(self,team,roster,position):
        for player in roster:
            currentPlayerPosition = self.data.playersData[team][player]
            if (currentPlayerPosition == position):
                return player
        return NO_PLAYER_IN_POSITION
    '''        
                
             
        