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

def printHelp ():
    print('.exit                  Exit this program')

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
    '.exit': exitProgram,
    '.help': printHelp
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

    if dotCommand:
        try:
            dotCommands[userInput]()
        except KeyError:
            error = 'Error: unknown command or invalid arguments:  "'
            error += userInput[1:-1]
            error += '". Enter ".help" for help'
            print(error)
    else:
        # strip all trailing whitespace and semicolon
        userInput = re.sub(r'\s*;*$', '', userInput)
        if not userInput == '':
            try:
                action = userInput.split(' ', 1)[0]
                queryString = userInput.split(' ', 1)[1]
                queryCommands[action](queryString)
            except:
                print('Error: near "%s": syntax error' %action)


