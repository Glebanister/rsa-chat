import re

def isMatch(string, pattern):
    return bool(re.match(pattern, string))

def getNumbersFromString(string):
    return [int(x) for x in re.findall(r'\b\d+\b', string)]

def throwPrefix(string, prefix):
    return re.split(prefix, string)[1]