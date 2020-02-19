#!/usr/bin/env python3

# Programming Assignment 1 - Metadata Management
# Author: Adam Landis

import os  # for writing directories and files
import shutil  # for writing directories and files
import re  # for using regular expressions

# Global Constants

DB_DIR = 'dbs'
INIT_DB = 'main'
DOT_COMMAND_REGEX = re.compile('^\.([a-z]*) *$', re.I)
QUERY_COMMAND_REGEX = re.compile('^(CREATE|DROP|USE|SELECT|ALTER) *([^;]*)[ ;]*|^[ ;]*(;)$', re.I)

# Global vars

active_database = 'main'  # set the initial active database to 'main'


# Function definitions

def init():
    global DB_DIR, INIT_DB
    db_path = os.path.join(DB_DIR, INIT_DB)
    if not os.path.isdir(DB_DIR):
        os.makedirs(db_path)
    else:
        if not os.path.isdir(db_path):
            os.mkdir(db_path)


# helper functions

def join_l(l, sep):
    """
    Joins a list (l) by some delimiter string (sep) into a new string.
    Credit: https://codereview.stackexchange.com/a/162814

    l -- The list to join into a string
    sep -- The string to "glue" the list elements together with
    """
    li = iter(l)
    string = str(next(li))
    for i in li:
        string += str(sep) + str(i)
    return string


# dot-command functions

def exit_program():
    """
    Exits the program
    """
    quit()


def print_help():
    """
    Prints all of the allowed dot-commands and their function
    """
    print('.exit                  Exit this program')


# query command functions

def create(query_string):
    """
    Initiates a CREATE command

    queryString -- the remaining query after the CREATE keyword
    """
    resource_types = {
        'database': create_database,
        'table': create_table
    }
    create_regex = re.compile('^(DATABASE|TABLE) *(.+)$', re.I)
    try:
        parsed_query = create_regex.match(query_string).groups()
        resource_type = parsed_query[0].lower()  # grab the resource keyword
        query_string = parsed_query[1]  # save the remaining query

        # call the appropriate function based on resource
        resource_types[resource_type](query_string)
    except AttributeError:
        print('Error: syntax error')


def drop(query_string):
    """
    Initiates a DROP command

    queryString -- the remaining query after the DROP keyword
    """
    resource_types = {
        'database': drop_database,
        'table': drop_table,
    }
    drop_regex = re.compile('^(DATABASE|TABLE) *(.+)$', re.I)
    try:
        parsed_query = drop_regex.match(query_string).groups()
        resource_type = parsed_query[0].lower()  # grab the resource keyword
        query_string = parsed_query[1]  # save the remaining query

        # call the appropriate function based on resource
        resource_types[resource_type](query_string)
    except:
        print('Error: syntax error')


def use(query_string):
    """
    Initiates a USE command

    query_string -- the remaining query after the USE keyword
    """
    global DB_DIR, active_database
    use_regex = re.compile('^[a-z0-9_-]+$', re.I)
    match = use_regex.match(query_string)
    if match is not None:
        db_name = query_string
        db_path = os.path.join(DB_DIR, db_name)
        if os.path.isdir(db_path):
            active_database = db_name
            print('Using database %s.' % db_name)
        else:
            print('!Failed to use database %s because it does not exist.' % db_name)
    else:
        print('Error: syntax error')


def select(query_string):
    """
    Initiates a SELECT command

    query_string -- the remaining query after the SELECT keyword
    """
    global DB_DIR, active_database

    select_regex = re.compile('^([a-z0-9_*-, ]+) *FROM *([a-z0-9_-]+)$', re.I)

    try:
        groups = select_regex.match(query_string).groups()
        columns = groups[0].strip()  # grab only the columns we want to select
        tbl_name = groups[1].strip()  # grab just the table name from the query
        tbl_path = os.path.join(DB_DIR, active_database, tbl_name)

        if os.path.exists(tbl_path):
            if columns == '*':  # if selecting all columns
                with open(tbl_path, 'r') as table_file:
                    print(table_file.read())  # just print the whole file
        else:
            print('!Failed to query table %s because it does not exist.' % tbl_name)

    except AttributeError:
        print('Error: syntax error')


def alter(query_string):
    """
    Initiates a ALTER command

    query_string -- the remaining query after the ALTER keyword
    """
    print('alter called with query_string = "%s"' % query_string)
    resource_types = {
        'table': alter_table,
    }
    alter_regex = re.compile('^(TABLE) *(.+)$', re.I)
    try:
        parsed_query = alter_regex.match(query_string).groups()
        resource_type = parsed_query[0].lower()  # grab the resource keyword
        query_string = parsed_query[1]  # save the remaining query

        # call the appropriate function based on resource
        resource_types[resource_type](query_string)
    except AttributeError:
        print('Error: syntax error near ')
    except IndexError:
        print('Error: syntax error')


def alter_table(query_string):
    """
    Alters a table

    query_string -- The remaining query after the ALTER TABLE keywords
    """
    print('alter_table called with query_string = "%s"' % query_string)
    alter_table_regex = re.compile('^([a-z0-9_-]+) *(ADD) *(.+)$', re.I)
    groups = alter_table_regex.match(query_string).groups()
    print('groups:', groups)
    tbl_name = groups[0]
    print('tbl_name: %s' % tbl_name)
    operation = groups[1]
    print('operation: %s' % operation)
    column = groups[2]
    print('column: %s' % column)

    tbl_path = os.path.join(DB_DIR, active_database, tbl_name)
    print('tbl_path: %s' % tbl_path)

    if os.path.exists(tbl_path):
        print('table %s exists!' % tbl_name)
        with open(tbl_path, 'a') as table_file:
            table_file.write(' | %s' % column)
    else:
        print('table %s does not exist!' % tbl_name)


def create_database(db_name):
    """
    Creates a database with the given name

    dbName -- the name of the database to create
    """
    global DB_DIR
    db_path = os.path.join(DB_DIR, db_name)  # create the path to the new database

    try:
        os.mkdir(db_path)
        print('Database %s created.' % db_name)
    except OSError:
        print('!Failed to create database %s because it already exists.' % db_name)


def create_table(query_string):
    """
    Creates a table with the given name

    query_string -- the remaining query string after CREATE TABLE keywords
    """
    global DB_DIR, active_database

    table_regex = re.compile('^([a-z0-9_-]+) *\((.*)\)$', re.I)
    groups = table_regex.match(query_string).groups()
    tbl_name = groups[0]

    try:
        # get the path to the active database
        tbl_path = os.path.join(DB_DIR, active_database, tbl_name)
        os.mknod(tbl_path)

        schema = groups[1]
        col_list = schema.split(',')  # split string up by column
        col_list = [col.strip() for col in col_list]  # strip surrounding whitespace
        col_str = join_l(col_list, ' | ')  # join list into string with sep " | "
        with open(tbl_path, 'w') as tbl_file:
            tbl_file.write(col_str)

        print('Table %s created.' % tbl_name)
    except OSError:
        print('!Failed to create table %s because it already exists.' % tbl_name)
    except IndexError:
        print('Error: syntax error near \'%s\'' % tbl_name)


def drop_database(db_name):
    """
    Drops a database with the given name

    db_name -- the name of the database to drop
    """
    global DB_DIR
    db_path = os.path.join(DB_DIR, db_name)  # create the path to the new database

    try:
        # recursively remove database (directory) and all tables (files)
        shutil.rmtree(db_path)
        print('Database %s dropped.' % db_name)
    except OSError:
        print('!Failed to database %s because it does not exist.' % db_name)


def drop_table(tbl_name):
    """
    Drops a table with the given name

    tbl_name -- the name of the table to drop
    """
    global DB_DIR, active_database

    try:
        # get the path to the active database
        tbl_path = os.path.join(DB_DIR, active_database, tbl_name)
        os.remove(tbl_path)

        print('Table %s dropped.' % tbl_name)
    except OSError:
        print('!Failed to drop table %s because it does not exist.' % tbl_name)


# Dot/Query Command Dictionaries

dot_commands = {
    '.exit': exit_program,
    '.help': print_help
}

query_commands = {
    'create': create,
    'drop': drop,
    'use': use,
    'select': select,
    'alter': alter
}

# Program start

init()  # create initial directory structure

# The main command prompt loop
while True:
    # reset our variables
    user_input = ''
    query_done = False
    is_dot_command = False

    while not query_done:
        # always append prior user input for multi-line support
        user_input += input('> ')

        # ignore comments
        if user_input[0:2] == '--':
            user_input = ''

        # determine if the input is a dot-command
        is_dot_command = DOT_COMMAND_REGEX.match(user_input) is not None

        if is_dot_command:
            break  # dot-commands aren't multi-line/multi-keyword, so bail
        else:
            # we're done collecting input if input is non-empty and last token is a ';'
            user_input = user_input.strip()  # strip all leading and trailing whitespace
            query_done = len(user_input) > 0 and user_input[-1] == ';'

            # if no ';', but input is non-empty, append a ' ' to delimit further input
            if not query_done and len(user_input) > 0:
                user_input += ' '

    if is_dot_command:
        try:
            user_input = user_input.lower()  # make dot-command case insensitive
            dot_commands[user_input]()  # try calling the dotCmds function keyed by userInput
        except KeyError:
            error = 'Error: unknown command or invalid arguments:  "'
            error += user_input[1:]  # strip off the '.'
            error += '". Enter ".help" for help'
            print(error)
    else:
        try:
            # parse the input into groups
            parsed_input = QUERY_COMMAND_REGEX.match(user_input).groups()

            # strip all elements which are None or ''
            parsed_input = list(filter(lambda x: x is not None and x != '', parsed_input))

            if parsed_input[0] != ';':
                action = parsed_input[0].lower()
                query_commands[action](parsed_input[1])
        except:
            print('Error: syntax error')
