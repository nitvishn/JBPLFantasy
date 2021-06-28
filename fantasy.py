from difflib import SequenceMatcher
from copy import deepcopy

#DEFINITION OF POINTS
goalDict={"GoalKeeper":7, "Defender":6, "Striker":5, "MidFielder":5}
assistPoints=3
tackleAndSaveDict={"GoalKeeper":1, "Defender":1, "Striker":0, "MidFielder":0}
redCardPenalty=-3
yellowCardPenalty=-1
cleanSheetDict={"GoalKeeper":4, "Defender":4, "Striker":0, "MidFielder":1}

#DEFINITION OF CLASSES
class Player(object):
    def __init__(self, name, position, isCaptain=False):

        assert type(name)==str

        self.points=0
        self.position=position
        self.isCaptain=isCaptain
        self.name=name
        self.cleanSheets=0
        self.redcards=0
        self.yellowcards=0
        self.tackles=0
        self.goals=0
        self.assists=0
        self.saves=0
        self.miscpoints=0

    def __str__(self):
        return self.name+' ('+type(self).__name__+'): '+str(self.getPoints())+" points (goals: "+str(self.goals)+", saves: "+str(self.saves)+", miscpoints: "+str(self.miscpoints)+", tackles: "+str(self.tackles)+')'

    def getPoints(self):
        position=self.position
        points=0
        points+=self.redcards*redCardPenalty
        points+=self.yellowcards*yellowCardPenalty
        points+=self.goals*goalDict[position]
        if(self.saves/2 >= 1):
            points+=int(self.saves/2)*tackleAndSaveDict[position]
        if (self.tackles / 2 >= 1):
            points += int(self.tackles / 2) * tackleAndSaveDict[position]
        points+=self.assists*assistPoints
        points+=self.cleanSheets*cleanSheetDict[position]
        points+=self.miscpoints
        points+=self.points
        return points

class Team(object):
    def __init__(self, name, players):
        self.players = players
        self.points = 0
        self.name = name

    def getPoints(self):
        acc=0
        for player in self.players:
            acc+=player.getPoints()
        return acc

    def __str__(self):
        return self.name

class RealTeam(Team):
    def __init__(self, name, players):
        Team.__init__(self, name, players)

class FantasyTeam(object):
    def __init__(self, name, email, playernames):
        self.playernames=playernames
        self.email=email
        self.name=name
        self.points=0

    def getPoints(self):
        tot=0
        players=realPlayers
        for playername in self.playernames:
            for player in players:
                if(player.name==playername):
                    tot+=player.getPoints()
        return tot+self.points

    def __str__(self):
        return self.name+', owned by '+self.email+', '+str(self.getPoints())+' points'

def getClosestPlayerName(playername):
    best=[None, 0]
    for player in realPlayers:
        if(similarity(playername, player.name)>=best[1]):
            best[1]=similarity(playername, player.name)
            best[0]=player.name
    return best[0]

def getTeam(playername):
    playername=getClosestPlayerName(playername)
    for team in realTeams:
        for player in team.players:
            if player.name==playername:
                return team.name

#FUNCTION DEFINITIONS
def updateScore(playerdata):
    playername=getClosestPlayerName(playerdata["name"])
    for player in realPlayers:
        if(player.name==playername):
            player.goals+=playerdata["goals"]
            player.tackles+=playerdata["tackles"]
            player.assists+=playerdata["assists"]
            player.saves+=playerdata["saves"]
            player.redcards+=playerdata["redcards"]
            player.yellowcards+=playerdata["yellowcards"]
            if(playerdata["time"]>=10):
                player.miscpoints+=2
            else:
                player.miscpoints+=1

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def processMatch(matchfile):

    def parsePlayerLine(inputline):
        line=inputline.split(",")
        if(len(line)!=8):
            raise IOError
        return deepcopy({"name":line[0], "goals":int(line[1]), "assists":int(line[2]), "time":float(line[3]), "tackles":int(line[4]), "saves":int(line[5]), "yellowcards":int(line[6]), "redcards":int(line[7])})

    file = open(matchfile, "r")
    realTeamsPlaying=[]
    cleanSheetDict={}
    for line in file:
        if(line[0]=="#"):
            continue
        line=line.replace("\n", "")
        if line in realTeamNames:
            realTeamsPlaying.append(line)
            cleanSheetDict[line]=True
            continue

        if len(line)>4:
            playerData=parsePlayerLine(line)
            if(playerData["goals"]>0):
                team1=getTeam(playerData["name"])
                for team2 in realTeamsPlaying:
                    if(team1!=team2):
                        cleanSheetDict[team2]=False
            updateScore(playerData)

    for key in cleanSheetDict:
        if cleanSheetDict[key]==True:
            for team in realTeams:
                if team.name==key:
                    for player in team.players:
                        player.cleanSheets+=1

def getRealTeamFromFile(teamname, filename):
    file=open(filename, "r")
    players=[]
    for line in file:
        name=line[3:]
        name=name.replace('\n', "")
        if(line[0]=='G'):
            players.append(Player(name, "GoalKeeper"))
        elif(line[0]=="D"):
            players.append(Player(name, "Defender"))
        elif(line[0]=="M"):
            players.append(Player(name, "MidFielder"))
        elif(line[0]=="S"):
            players.append(Player(name, "Striker"))
        else:
            raise IOError
        if(line[1]==";"):
            players[-1].isCaptain=True
    return RealTeam(teamname, players)

def extractPlayers(teams):
    players=[]
    for team in teams:
        for player in team.players:
            players.append(player)
    return players

def getFantasyTeams(filename):
    players=realPlayers
    file = open(filename, "r")
    rawteamlist=[]
    for line in file:
        if(len(line.split(','))<8):
            continue
        if(line[0]=="#"):
            continue
        line=line.split(',')
        newline=[]
        for string in line:
            newstring=string
            if(newstring[0:1] == ' '):
                newstring=newstring[1:]
            if(newstring[-1:]==' '):
                newstring=newstring[:-1]
            newline.append(newstring)
        rawteamlist.append(newline)

    stringteamlist=[]
    for team in rawteamlist:
        newteam=[team[0], team[1]]
        team=team[2:]
        for string in team:
            best=[None, 0]
            for player in realPlayers:
                if(similarity(player.name, string)>best[1]):
                    best[1]=similarity(player.name, string)
                    best[0]=player.name
            newteam.append(best[0])
        stringteamlist.append(newteam)

    teamlist=[]
    for team in stringteamlist:
        teamlist.append(FantasyTeam(team[0], team[1], team[2:]))

    return teamlist

fearcontrol=getRealTeamFromFile("fearcontrol", "realTeams/fearcontrol.txt")
spacemonkeymafia=getRealTeamFromFile("spacemonkeymafia", "realTeams/spacemonkeymafia.txt")
spicefc=getRealTeamFromFile("spicefc", "realTeams/spicefc.txt")
error404=getRealTeamFromFile("error404", "realTeams/error404.txt")
mcwingers=getRealTeamFromFile("mercurialwingers", "realTeams/mcwingers.txt")
thunderwarriors=getRealTeamFromFile("thunderwarriors", "realTeams/thunderwarriors.txt")
bombsquad=getRealTeamFromFile("bombsquad", "realTeams/bombsquad.txt")
skullcrushers=getRealTeamFromFile("skullcrushers", "realTeams/skullcrushers.txt")

#DEFINITION OF TEAMS
realTeams=[fearcontrol, spacemonkeymafia, spicefc, error404, mcwingers, thunderwarriors, bombsquad, skullcrushers]
realTeamNames=["fearcontrol", "spacemonkeymafia", "spicefc", "error404", "mcwingers", "thunderwarriors", "bombsquad", "skullcrushers"]
realPlayers=extractPlayers(realTeams)

processMatch("matches/match1.txt")

fantasyteams=getFantasyTeams("fantasyTeams.csv")
fantasyteams.sort(key=FantasyTeam.getPoints)

for team in fantasyteams:
    if team.email=="apratyay@tisb.ac.in":
        team.points=-(fantasyteams[-1].getPoints()-team.getPoints())

fantasyteams.sort(key=FantasyTeam.getPoints)

for team in fantasyteams:
    print(team)
    print()
    for player in team.playernames:
        for player2 in realPlayers:
            if(player==player2.name):
                print(player2)
    print()