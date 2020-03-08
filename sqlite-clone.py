#!/usr/bin/env python3

# Programming Assignment 1 - Metadata Management
#
# Author: Adam Landis
# Date: 03/12/2020
# History:
# - 02/20/2020 -- Completed implementation of all metadata functionality (e.g. creating and
#   dropping databases and tables, using, altering, and querying tables, etc.)

import os  # for writing directories and files
import shutil  # for writing directories and files
import re  # for using regular expressions
import csv  # for working with comma-delimited files

# Global Constants

DB_DIR = 'dbs'
INIT_DB = 'main'
DOT_COMMAND_REGEX = re.compile('^\.([a-z]*) *$', re.I)
QUERY_COMMAND_REGEX = re.compile('^(CREATE|DROP|USE|SELECT|ALTER|INSERT|UPDATE|DELETE) *([^;]*)[ ;]*|^[ ;]*(;)$', re.I)

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


def parse_kv_pair_str(kv_pair_str):
    """
    Parses a key/value pair string (e.g. "key1 = val1, key2 = val2, ...") into
    a list of dictionaries consisting of each key/value pair.

    kv_pair_str -- The string of key value pairs to parse

    Returns a list dictionaries consisting of the key value pairs
    """
    kv_pairs_lst = kv_pair_str.split(',')  # split the string on commas
    kv_pairs_lst = [pair.strip() for pair in kv_pairs_lst]  # strip surrounding whitespace
    kv_pairs_lst = [re.sub('[\'"]', '', pair) for pair in kv_pairs_lst]  # remove quotation marks
    kv_tuples_lst = [tuple(re.split(' *= *', pair)) for pair in kv_pairs_lst]
    return [{'key': key, 'value': value} for (key, value) in kv_tuples_lst]


def parse_where_clause(clause):
    """
    Parses a WHERE clause in a query string into a dictionary and returns it
    :param clause: The portion of the query relating to the WHERE clause
    :return: The dictionary containing the parsed WHERE clause
    """
    where_regex = re.compile('^(.*) +(=|>|<|>=|<=|<>|LIKE|IN|BETWEEN) +(.*)$', re.I)
    groups = where_regex.match(clause).groups()
    return {
        'key': groups[0],
        'operator': groups[1],
        'value': re.sub('[\'"]', '', groups[2])  # strip away all quotes
    }


def read_header_from(table):
    """
    Reads the header from the given table and returns it as a string. If the
    file doesn't exist, returns an empty string.

    :param table: The name of the table to read the header from
    :return: The table header as a string, or empty string file doesn't exist
    """
    global DB_DIR, active_database
    try:
        assert len(table) > 0
    except AssertionError:
        print('ERROR: table argument must not be empty!')
        return ''
    tbl_path = os.path.join(DB_DIR, active_database, table)
    header = ''
    if os.path.exists(tbl_path):
        with open(tbl_path, 'r') as table_file:
            table_file.seek(0)  # make sure we're at beginning of file
            header = table_file.readline().strip('\n')
            try:
                assert len(header) > 0
            except AssertionError:
                print('ERROR: table header is empty!')
            table_file.close()
            return header
    print('Error: Table "%s" doesn\'t exist!' % table)
    return ''


def extract_model_from(header):
    """
    Extracts the model from a given table header

    :param header: The table header to extract the model from (string)
    :return: A list of dicts representing the table model
    """
    try:
        assert len(header) > 0
    except AssertionError:
        print('ERROR: header must not be empty!')
        return []
    model = []
    cast_func = {
        'int': int,
        'float': float,
        'double': float,
        'varchar': str,
        'char': str,
        'bool': bool,
        'boolean': bool
    }
    for col in header.split(','):
        try:
            col_split = col.split(' ', 1)
            col_name = col_split[0]
            data_type = col_split[1].split('(')[0]
        except IndexError:
            print('ERROR: header is not in proper format!')
            return []
        try:
            cast = cast_func[data_type]
        except KeyError:
            print('ERROR: cast function not found for data_type "%s"!' % data_type)
            return []
        model.append({
            'col_name': col_name,
            'data_type': data_type,
            'cast': cast
        })
    return model


def cond_func(operator):
    """
    Returns the appropriate condition function given the operator in a WHERE
    clause.

    e.g. If a query contains the '... WHERE age <= 32 ...' Then, the '<=' would
    be passed to this function and `lambda x, y: x <= y` would be returned for
    use outside the function.

    :param operator: A string representing the operator in the WHERE clause
    :return: The condition function
    """
    return {
        '=': lambda x, y: x == y,
        '>': lambda x, y: x > y,
        '<': lambda x, y: x < y,
        '>=': lambda x, y: x >= y,
        '<=': lambda x, y: x <= y,
        '<>': lambda x, y: x != y,
        'like': lambda x, y: False,  # todo need to implement LIKE lambda
        'in': lambda x, y: False,  # todo need to implement IN lambda
        'between': lambda x, y: False  # todo need to implement BETWEEN lambda
    }[operator]


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
    # strip all single & double quotes and split on ','
    values_lst = re.sub(r'[\'"]', '', values_str).split(',')
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

    update_regex = re.compile("^([a-zA-Z0-9_-]+) +SET +(.*) +WHERE +(.*)$", re.I)
    groups = update_regex.match(query_string).groups()
    tbl_name = groups[0].lower()
    kv_pairs_str = groups[1]
    condition_str = groups[2]
    set_dicts = parse_kv_pair_str(kv_pairs_str)
    where_dict = parse_where_clause(condition_str)
    tbl_path = os.path.join(DB_DIR, active_database, tbl_name)
    if os.path.exists(tbl_path):
        new_rows = []

        # Read the header to determine the table model for casting values to the
        # appropriate data type
        header = read_header_from(tbl_name)
        model = extract_model_from(header)

        # Extract just the column names from the model
        col_names = [item['col_name'] for item in model]

        # Using the key/value pairs given in the SET clause, find the column
        # numbers they correspond to and add them to each dictionary
        for idx, dict in enumerate(set_dicts):
            set_dicts[idx]['col'] = None
            if dict['key'] in col_names:
                set_dicts[idx]['col'] = col_names.index(dict['key'])

        # Using the key from the key/operator/value group from the WHERE clause
        # of the query, find the column it relates to and add it
        where_dict['col'] = None
        if where_dict['key'] in col_names:
            where_dict['col'] = col_names.index(where_dict['key'])

        # Update the rows which match the WHERE clause and columns defined by
        # SET clause of the query.
        with open(tbl_path, 'r') as table_file:
            table_file.seek(0)  # make sure we're at beginning of file
            tbl_reader = csv.reader(table_file)
            row_num = 0
            for row in tbl_reader:
                if row_num == 0:  # header row
                    new_rows.append(row.copy())
                else:
                    new_row = row.copy()
                    col = where_dict['col']
                    validator = cond_func(where_dict['operator'])
                    cast_func = model[col]['cast']
                    lhs = cast_func(row[col])
                    rhs = cast_func(where_dict['value'])
                    if validator(lhs, rhs):
                        for dict in set_dicts:
                            new_row[dict['col']] = dict['value']
                    new_rows.append(new_row)
                row_num += 1
            table_file.close()
        with open(tbl_path, 'w') as table_file:
            table_writer = csv.writer(table_file)
            for row in new_rows:
                table_writer.writerow(row)
            table_file.close()
    else:
        print('!Failed to query table %s because it does not exist.' % tbl_name)


def delete(query_string):
    """
    Initiates a DELETE command

    :param query_string: the remaining query after the DELETE keyword
    """
    global DB_DIR, active_database

    delete_regex = re.compile('^FROM ([a-z0-9_-]+) WHERE (.+)$', re.I)
    groups = delete_regex.match(query_string).groups()
    tbl_name = groups[0].lower()
    where_clause = groups[1]
    where_dict = parse_where_clause(where_clause)
    tbl_path = os.path.join(DB_DIR, active_database, tbl_name)
    if os.path.exists(tbl_path):
        new_rows = []

        # Read the header to determine the table model for casting values to the
        # appropriate data type
        header = read_header_from(tbl_name)
        model = extract_model_from(header)

        # Extract just the column names from the model
        col_names = [item['col_name'] for item in model]

        # Using the key from the key/operator/value group from the WHERE clause
        # of the query, find the column it relates to and add it
        where_dict['col'] = None
        if where_dict['key'] in col_names:
            where_dict['col'] = col_names.index(where_dict['key'])

        # Only keep the rows which don't match the WHERE clause
        with open(tbl_path, 'r') as table_file:
            table_file.seek(0)  # make sure we're at beginning of file
            tbl_reader = csv.reader(table_file)
            row_num = 0
            for row in tbl_reader:
                if row_num == 0:  # header row
                    new_rows.append(row.copy())
                else:
                    new_row = row.copy()
                    col = where_dict['col']
                    validator = cond_func(where_dict['operator'])
                    cast_func = model[int(col)]['cast']
                    lhs = cast_func(row[col])
                    rhs = cast_func(where_dict['value'])
                    if validator(lhs, rhs) is False:
                        new_rows.append(new_row)
                row_num += 1
            table_file.close()
        with open(tbl_path, 'w') as table_file:
            table_writer = csv.writer(table_file)
            for row in new_rows:
                table_writer.writerow(row)
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
    'update': update,
    'delete': delete
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
