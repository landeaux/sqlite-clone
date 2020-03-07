#!/usr/bin/env python3

# Programming Assignment 1 - Metadata Management
#
# Author: Adam Landis
# Date: 02/20/2020
# History:
# - Completed implementation of all metadata functionality (e.g. creating and
#   dropping databases and tables, using, altering, and querying tables, etc.)

import os  # for writing directories and files
import shutil  # for writing directories and files
import re  # for using regular expressions

# Global Constants

DB_DIR = 'dbs'
INIT_DB = 'main'
DOT_COMMAND_REGEX = re.compile('^\.([a-z]*) *$', re.I)
QUERY_COMMAND_REGEX = re.compile('^(CREATE|DROP|USE|SELECT|ALTER|INSERT|UPDATE) *([^;]*)[ ;]*|^[ ;]*(;)$', re.I)

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
    print('All done.')
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
    match = use_regex.match(query_string)  # match the query_string against the regex

    if match is not None:
        db_name = query_string  # for USE commands, the remaining query is the db name
        db_path = os.path.join(DB_DIR, db_name)  # generate the file path to the db
        if os.path.isdir(db_path):  # if the file path to the database exists
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
        tbl_name = groups[1].strip().lower()  # grab table name and convert to lowercase
        tbl_path = os.path.join(DB_DIR, active_database, tbl_name)

        if os.path.exists(tbl_path):
            if columns == '*':  # if selecting all columns
                with open(tbl_path, 'r') as table_file:
                    table_file.seek(0)  # make sure we're at beginning of file
                    for line in table_file.readlines():
                        # reformat comma-delimited line into ' | ' delimited output
                        output = ' | '.join(line.split(',')).strip('\n')
                        print(output)
                    table_file.close()
        else:
            print('!Failed to query table %s because it does not exist.' % tbl_name)

    except AttributeError:
        print('Error: syntax error')


def insert(query_string):
    """
    Initiates an INSERT command

    query_string -- the remaining query after the INSERT keyword
    """
    global DB_DIR, active_database

    insert_regex = re.compile('^INTO +([a-zA-Z0-9_-]+) +VALUES *\((.*)\)$', re.I)
    groups = insert_regex.match(query_string).groups()
    tbl_name = groups[0].lower()
    values_str = groups[1]
    values_lst = re.sub(r'[\'"]', '', values_str).split(',')  # strip all single & double quotes and split on ','
    values_lst = [el.strip() for el in values_lst]  # strip surrounding whitespace
    tbl_path = os.path.join(DB_DIR, active_database, tbl_name)
    if os.path.exists(tbl_path):
        with open(tbl_path, 'a+') as table_file:
            line = ','.join(values_lst)  # rejoin value list as comma-delimited list
            table_file.write('\n%s' % line)  # append the line as a new row in the file
            print('1 new record inserted.')
            table_file.close()
    else:
        print('!Failed to query table %s because it does not exist.' % tbl_name)


def update(query_string):
    """
    Initiates an UPDATE command

    query_string -- the remaining query after the UPDATE keyword
    """
    global DB_DIR, active_database

    print('update query called with query_string = %s' % query_string)
    update_regex = re.compile("^([a-zA-Z0-9_-]+) +SET +(.*) +WHERE +(.*)$", re.I)
    groups = update_regex.match(query_string).groups()
    tbl_name = groups[0].lower()
    kv_pairs_str = groups[1]
    condition = groups[2]
    print('tbl_name = %s' % tbl_name)
    print('kv_pairs_str = %s' % kv_pairs_str)
    print('condition = %s' % condition)
    tbl_path = os.path.join(DB_DIR, active_database, tbl_name)
    if os.path.exists(tbl_path):
        with open(tbl_path, 'r') as table_file:
            table_file.seek(0)
            col = -1
            row = 0
            for line in table_file.readlines():
                print('current line is %s' % line)
                if row == 0:
                    line_lst = line.split(',')
                    print('line_lst =', line_lst)
                    for idx, val in enumerate(line_lst):
                        if re.match('^name .*$', val, re.I) is not None:
                            col = idx
                    print('column found at idx = %s' % col)
                row += 1
            table_file.close()
    else:
        print('!Failed to query table %s because it does not exist.' % tbl_name)


def alter(query_string):
    """
    Initiates a ALTER command

    query_string -- the remaining query after the ALTER keyword
    """
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
        print('Error: syntax error')
    except IndexError:
        print('Error: syntax error')


def alter_table(query_string):
    """
    Alters a table

    query_string -- The remaining query after the ALTER TABLE keywords
    """
    operations = {
        'add': alter_table_add_column
    }
    alter_table_regex = re.compile('^([a-z0-9_-]+) *(ADD) *(.+)$', re.I)
    try:
        groups = alter_table_regex.match(query_string).groups()
        tbl_name = groups[0]  # store the table name from the query
        operation = groups[1].lower()  # store the operation (e.g ADD) from the query
        column = groups[2]  # store the column from the query

        tbl_path = os.path.join(DB_DIR, active_database, tbl_name)

        if os.path.exists(tbl_path):  # if the file path to the table exists
            operations[operation](tbl_path, column)  # call the appropriate handler
            print('Table %s modified' % tbl_name)
        else:
            print('!Failed to query table %s because it does not exist.' % tbl_name)
    except AttributeError:
        print('Error: syntax error')


def alter_table_add_column(tbl_path, column):
    """
    Alters a table by adding the specified column

    tbl_path -- The file path to the table
    column -- The column to add to the table
    """
    with open(tbl_path, 'a') as table_file:
        table_file.write(',%s' % column)  # append the column to the file header
        table_file.close()


def create_database(db_name):
    """
    Creates a database with the given name

    dbName -- the name of the database to create
    """
    global DB_DIR
    db_path = os.path.join(DB_DIR, db_name)  # create the path to the new database

    try:
        os.mkdir(db_path)  # make a directory for the database
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
    tbl_name = groups[0].lower()

    try:
        # get the path to the active database
        tbl_path = os.path.join(DB_DIR, active_database, tbl_name)
        os.mknod(tbl_path)  # make a file in the active database directory

        schema = groups[1]  # store the schema (i.e. the columns and their data types)
        col_list = schema.split(',')  # split string up by column
        col_list = [col.strip() for col in col_list]  # strip surrounding whitespace
        col_str = join_l(col_list, ',')  # join list into string with sep ","
        with open(tbl_path, 'w') as table_file:
            table_file.write(col_str)  # write the first line as the columns of the table
            table_file.close()

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
        print('Database %s deleted.' % db_name)
    except OSError:
        print('!Failed to delete %s because it does not exist.' % db_name)


def drop_table(tbl_name):
    """
    Drops a table with the given name

    tbl_name -- the name of the table to drop
    """
    global DB_DIR, active_database

    try:
        # get the path to the active database
        tbl_path = os.path.join(DB_DIR, active_database, tbl_name)
        os.remove(tbl_path)  # remove the file from the active db directory

        print('Table %s deleted.' % tbl_name)
    except OSError:
        print('!Failed to delete table %s because it does not exist.' % tbl_name)


# Dot/Query Command Dictionaries (these map commands to their appropriate handler)

dot_commands = {
    '.exit': exit_program,
    '.help': print_help
}

query_commands = {
    'create': create,
    'drop': drop,
    'use': use,
    'select': select,
    'alter': alter,
    'insert': insert,
    'update': update
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

        user_input = user_input.strip()  # strip all surrounding whitespace

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
