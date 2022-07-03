import random

def getlines(filename):
    
    textdump = open(filename, "r")
    line_list = []
    
    for line in textdump.readlines():
        if line != '\n':
            line_list.append(line.strip())
    
    textdump.close()
    
    return line_list


def quotation():
    quotes = getlines("hamlet.txt")
    
    allowed_quotes = []
    
    for quote in quotes:
        if not censor(quote):
            allowed_quotes.append(quote)
            
#    print(len(quotes), len(allowed_quotes))        
    return random.choice(allowed_quotes)


denylist = getlines("denylist.txt")
def censor(checkstring):
    checklist = checkstring.split()
    for word in checklist:
        if word.lower() in denylist:
            return True    
    return False
            
#print(quotation())

#def censor(string):




