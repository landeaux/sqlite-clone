#!/usr/bin/env python

import os

quitting = False

def parseInput (input):
    print('parseInput() called with input: ', input)

def createDatabase (dbName):
    print('createDatabase() called with dbName: ', dbName)
    parentPath = os.getcwd()
    directory = dbName
    fullPath = os.path.join(parentPath, directory)
    os.mkdir(fullPath)
    print('database created at ', fullPath)

while not quitting:
    userInput = raw_input('> ')

    if userInput == 'exit':
        quitting = True

    if userInput == 'CREATE DATABASE test':
        createDatabase('test')

