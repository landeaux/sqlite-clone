#!/usr/bin/env python3

# Programming Assignment 1 - Metadata Management
# Author: Adam Landis

import os, shutil # for writing directories and files
import re # for using regular expressions

def parseInput (input):
    print('parseInput() called with input: ', input)

############################## dot-command functions ##############################

def exitProgram ():
    """
    Exits the program
    """
    quit()

def printHelp ():
    """
    Prints all of the allowed dot-commands and their function
    """
    print('.exit                  Exit this program')

###################################################################################

############################# query command functions #############################

def create (queryString):
    """
    Initiates a CREATE command

    queryString -- the remaining query after the CREATE keyword
    """
    resourceTypes = {
        'database': createDatabase
    }
    resourceType = queryString.split(' ', 1)[0] # grab the resource keyword
    resourceType = resourceType.lower() # convert resource keyword to lowercase
    queryString = queryString.split(' ', 1)[1] # save the remaining query
    resourceTypes[resourceType](queryString) # call the appropriate function based on resource

def drop (queryString):
    """
    Initiates a DROP command

    queryString -- the remaining query after the DROP keyword
    """
    resourceTypes = {
        'database': dropDatabase
    }
    resourceType = queryString.split(' ', 1)[0] # grab the resource keyword
    resourceType = resourceType.lower() # convert resource keyword to lowercase
    queryString = queryString.split(' ', 1)[1] # save the remaining query
    resourceTypes[resourceType](queryString) # call the appropriate function based on resource

def createDatabase (dbName):
    """
    Creates a database with the given name

    dbName -- the name of the database to create
    """
    parentPath = os.getcwd() # get the current working directory path
    directory = dbName
    fullPath = os.path.join(parentPath, directory) # join with dbName to get full path
    try:
        os.mkdir(fullPath)
        print('Database %s created.' % dbName)
    except OSError:
        print('!Failed to create database %s because it already exists.' % dbName)

def dropDatabase (dbName):
    """
    Drops a database with the given name

    dbName -- the name of the database to drop
    """
    parentPath = os.getcwd() # get the current workgin directory path
    directory = dbName
    fullPath = os.path.join(parentPath, directory) # join with dbName to get full path
    try:
        # recursively remove database (directory) and all tables (files)
        shutil.rmtree(fullPath)
        print('Database %s dropped.' % dbName)
    except OSError:
        print('!Failed to database %s because it does not exist.' % dbName)

###################################################################################

dotCmds = {
    '.exit': exitProgram,
    '.help': printHelp
}

dotCmdRegex = re.compile('^\.([a-z]*) *$', re.I)

queryCommands = {
    'create': create,
    'drop': drop
}

# The main command prompt loop
while True:
    # reset our variables
    userInput = ''
    queryDone = False
    isDotCmd = False

    while not queryDone:
        # always append prior user input for multiline support
        userInput += input('> ');

        # determine if the input is a dot-command
        isDotCmd = dotCmdRegex.match(userInput) != None

        if isDotCmd:
            break # dot-commands aren't multiline/multi-keyword, so bail
        else:
            # we're done collecting input if input is non-empty and last token is a ';'
            userInput = userInput.strip() # strip all leading and trailing whitespace
            queryDone = len(userInput) > 0 and userInput[-1] == ';'

            # if no ';', but input is non-empty, append a ' ' to delimit further input
            if not queryDone and len(userInput) > 0:
                userInput += ' '

    if isDotCmd:
        try:
            userInput = userInput.lower() # make dot-command case insensitive
            dotCmds[userInput]() # try calling the dotCmds function keyed by userInput
        except KeyError:
            error = 'Error: unknown command or invalid arguments:  "'
            error += userInput[1:] # strip off the '.'
            error += '". Enter ".help" for help'
            print(error)
    else:
        regex = re.compile('^ *(CREATE|DROP|USE|SELECT|ALTER){0,1} *([^;]*)(;)[ ;]*$', re.I)

        # parse the input into groups
        parsedInput = regex.match(userInput).groups()

        # strip all elements which are None or ''
        parsedInput = list(filter(lambda x: x != None and x != '', parsedInput))
        print(parsedInput)
        if parsedInput[0] != ';':
            try:
                print(parsedInput)
                action = parsedInput[0].lower()
                queryCommands[action](parsedInput[1])
            #except AttributeError:
            #    print('no groups')
            except IndexError:
                print('invalid command %s' % action)
