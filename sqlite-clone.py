#!/usr/bin/env python3

# Programming Assignment 1 - Metadata Management
# Author: Adam Landis

import os, shutil # for writing directories and files
import re # for using regular expressions

DB_DIR = 'dbs'
INIT_DB = 'main'

def init ():
    dbPath = os.path.join(DB_DIR, INIT_DB)
    if not os.path.isdir(DB_DIR):
        os.makedirs(dbPath)
    else:
        if not os.path.isdir(dbPath):
            os.mkdir(dbPath)

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

def use (queryString):
    """
    Initiates a USE command

    queryString -- the remaining query after the USE keyword
    """
    regex = re.compile('^[a-z0-9_-]+$', re.I)
    match = regex.match(queryString)
    if match != None:
        dbName = queryString
        dbPath = os.path.join(DB_DIR, dbName)
        if os.path.isdir(dbPath):
            activeDb = dbName
            print('Using database %s.' %dbName)
        else:
            print('!Failed to use database %s because it does not exist.' %dbName)

def createDatabase (dbName):
    """
    Creates a database with the given name

    dbName -- the name of the database to create
    """
    dbPath = os.path.join(DB_DIR, dbName) # create the path to the new database 

    try:
        os.mkdir(dbPath)
        print('Database %s created.' % dbName)
    except OSError:
        print('!Failed to create database %s because it already exists.' %dbName)

def dropDatabase (dbName):
    """
    Drops a database with the given name

    dbName -- the name of the database to drop
    """
    dbPath = os.path.join(DB_DIR, dbName) # create the path to the new database

    try:
        # recursively remove database (directory) and all tables (files)
        shutil.rmtree(dbPath)
        print('Database %s dropped.' % dbName)
    except OSError:
        print('!Failed to database %s because it does not exist.' %dbName)

###################################################################################

dotCmds = {
    '.exit': exitProgram,
    '.help': printHelp
}

dotCmdRegex = re.compile('^\.([a-z]*) *$', re.I)

queryCommands = {
    'create': create,
    'drop': drop,
    'use': use
}

init() # create initial directory structure
activeDb = 'main' # set the initial active database to 'main'

# The main command prompt loop
while True:
    # reset our variables
    userInput = ''
    queryDone = False
    isDotCmd = False

    while not queryDone:
        # always append prior user input for multiline support
        userInput += input('> ');

        # ignore comments
        if userInput[0:2] == '--':
            userInput = ''

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
        regex = re.compile('^(CREATE|DROP|USE|SELECT|ALTER) *([^;]*)[ ;]*|^[ ;]*(;)$', re.I)

        try:
            # parse the input into groups
            parsedInput = regex.match(userInput).groups()

            # strip all elements which are None or ''          
            parsedInput = list(filter(lambda x: x != None and x != '', parsedInput))

            if parsedInput[0] != ';':
                action = parsedInput[0].lower()
                queryCommands[action](parsedInput[1])
        except:
            print('Error: syntax error')

