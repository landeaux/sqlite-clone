#!/usr/bin/env python

quitting = False

def parseInput (input):
    print('parseInput() called with input: ', input)

def createDatabase (dbName):
    print('createDatabase() called with dbName:', dbName)

while not quitting:
    userInput = raw_input('> ')

    if userInput == 'exit':
        quitting = True

    if userInput == 'CREATE DATABASE test':
        createDatabase('test')

