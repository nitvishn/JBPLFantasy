import csv

csvfile=open("fantasyTeams.csv", "r")
csvWriter=csv.reader(csvfile, delimiter=",")
# line=["#TEAMNAME", "#EMAIL", "#GOALKEEPER", "DEF1", "DEF2", "MID1", "MID2", "STRIKER (THE BEST TRACER PLAYER IN THE WORLD)", "CAPTAIN"]
for line in csvfile:
	print(line)