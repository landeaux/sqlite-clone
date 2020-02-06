#!/usr/bin/env python

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

def delete (queryString):
    """
    Initiates a DELETE command

    queryString -- the remaining query after the DELETE keyword
    """
    resourceTypes = {
        'database': deleteDatabase
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

def deleteDatabase (dbName):
    """
    Deletes a database with the given name

    dbName -- the name of the database to delete
    """
    parentPath = os.getcwd() # get the current workgin directory path
    directory = dbName
    fullPath = os.path.join(parentPath, directory) # join with dbName to get full path
    try:
        # recursively remove database (directory) and all tables (files)
        shutil.rmtree(fullPath)
        print('Database %s deleted.' % dbName)
    except OSError:
        print('!Failed to database %s because it does not exist.' % dbName)

###################################################################################

dotCommands = {
    '.exit': exitProgram,
    '.help': printHelp
}

queryCommands = {
    'create': create,
    'delete': delete
}

# The main command prompt loop
while True:
    # reset our variables
    userInput = ''
    queryDone = False
    dotCommand = False

    while not queryDone:
        # always append prior user input for multiline support
        userInput += raw_input('> ');

        # determine if the input is a dot-command
        dotCommand = len(userInput) > 0 and userInput[0] == '.'

        if dotCommand:
            break # dot-commands aren't multiline/multi-keyword, so bail
        else:
            # we're done collecting input if input is non-empty and last token is a ';'
            queryDone = len(userInput) > 0 and userInput[-1] == ';'

            # if no ';', but input is non-empty, append a ' ' to delimit further input
            if not queryDone and len(userInput) > 0:
                userInput += ' '

    if dotCommand:
        try:
            userInput = userInput.lower() # make dot-command case insensitive
            dotCommands[userInput]() # try calling the dotCommand function keyed by input
        except KeyError:
            error = 'Error: unknown command or invalid arguments:  "'
            error += userInput[1:-1] # strip off the '.'
            error += '". Enter ".help" for help'
            print(error)
    else:
        # strip all trailing whitespace and semicolon
        userInput = re.sub(r'\s*;*$', '', userInput)

        # if stripping trailing whitespace and semicolon still leaves us with input
        if not userInput == '':
            try:
                action = userInput.split(' ', 1)[0] # grab the first keyword (action)
                action = action.lower() # convert the action to lowercase
                queryString = userInput.split(' ', 1)[1] # store the remaining query for parsing
                queryCommands[action](queryString) # call the query function keyed by action
            except:
                print('Error: near "%s": syntax error' %action)


