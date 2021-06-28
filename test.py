from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

inpt=input("Enter name of player: ")
file = open("prices.txt", "r")
lines=[]
currentTag=None
for line in file:
    newline=""
    if(line[0]=='#'):
        currentTag=line
    for char in line:
        if(char=='0'):
            continue
        if(char=='#'):
            currentTag=line
            continue
        if(char.isalpha()):
            newline+=char.upper()
            continue
        newline+=char
    if(inpt in line or inpt.upper() in line):
        print(currentTag)
        print(line)
        break
    lines.append(newline)