#!/usr/bin/env python

quitting = False

def createDatabase ():
    print('createDatabase() called')

while not quitting:
    userInput = raw_input('> ')

    if userInput == 'exit':
        quitting = True

