#!/usr/bin/env python

import os
import re

def parseInput (input):
    print('parseInput() called with input: ', input)

def createDatabase (dbName):
    parentPath = os.getcwd()
    directory = dbName
    fullPath = os.path.join(parentPath, directory)
    try:
        os.mkdir(fullPath)
        print('Database %s created.' % dbName)
    except OSError:
        print('!Failed to create database %s because it already exists.' % dbName)

def exitProgram ():
    quit()

def create (queryString):
    resourceTypes = {
        'DATABASE': createDatabase
    }
    resourceType = queryString.split(' ', 1)[0]
    queryString = queryString.split(' ', 1)[1]
    print('resourceType: %s' % resourceType)
    print('queryString: %s' % queryString)
    resourceTypes[resourceType](queryString)

quitting = False

dotCommands = {
    '.exit': exitProgram
}

queryCommands = {
    'CREATE': create
}

while not quitting:
    userInput = ''
    queryDone = False
    dotCommand = False

    while not queryDone:
        userInput = userInput + raw_input('> ');
        dotCommand = len(userInput) > 0 and userInput[0] == '.'

        if dotCommand:
            break
        else:
            queryDone = len(userInput) > 0 and userInput[-1] == ';'
            if not queryDone and len(userInput) > 0:
                userInput = userInput + ' '

        print('userInput:', userInput)
        print('queryDone:', queryDone)

    if dotCommand:
        try:
            dotCommands[userInput]()
        except KeyError:
            print('%s is not a valid command!' % userInput)
    else:
        # strip all trailing whitespace and semicolon
        userInput = re.sub(r'\s*;*$', '', userInput)
        if not userInput == '' and not userInput.find(' ') == -1:
            try:
                action = userInput.split(' ', 1)[0]
                queryString = userInput.split(' ', 1)[1]
                queryCommands[action](queryString)
            except KeyError:
                print('\'%s\' is not a valid command!' % userInput)



