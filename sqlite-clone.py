#!/usr/bin/env python

import os

quitting = False

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

while not quitting:
    userInput = raw_input('> ')

    if userInput == 'exit':
        quitting = True

    if userInput == 'CREATE DATABASE test':
        createDatabase('test')

