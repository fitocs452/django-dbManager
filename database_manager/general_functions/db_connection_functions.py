import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

import MySQLdb

"""
    Purpose: Parse the SQL to get the headers of data
    Return: Array with headers
"""
def parseSQL(query, cursor):
    query = query.lower()
    # Database connection
    # cursor = connection.cursor()

    # Query to select columns from tables (if not defined in select statement)
    columnNameQuery = "SELECT column_name FROM information_schema.columns WHERE table_name='%s'"

    fieldsSelected = find_between(query, 'select', 'from')

    # Here we evaluate if is necessary to get the column names
    if ('*' in fieldsSelected):
        tables = extract_tables(query)
        fieldsSelected = []
        for table in tables:
            # We set the table parameter to the query to extract column names
            columnsSelectQuery = columnNameQuery % table
            cursor.execute(columnsSelectQuery)
            headers = cursor.fetchall()

            fieldsSelected = fieldsSelected + list(headers)

        # Is probably that we have tuples so we normalized them
        fieldsSelected = normalizeColumnNames(fieldsSelected)

        return fieldsSelected

    # If we have specific fields to select
    else:
        fieldsSelected = fieldsSelected.replace(" ", "")
        columns = fieldsSelected.split(',')

        fieldsSelected = []

        # We evaluate if each field has alias or not
        for column in columns:
            # if has alias, we show the alias
            if ('as' in column):
                index = column.index('as') + 2
                column = column[index:]

            # if not we show the field as in database
            fieldsSelected.append(column)

        return fieldsSelected

"""
    Purpose: Get a substring of 's' between 'first' and 'last'
    Return: A substring if possible, if not retunrn '*'
"""
def find_between(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return "*"

def is_subselect(parsed):
    if not parsed.is_group():
        return False
    for item in parsed.tokens:
        if item.ttype is DML and item.value.upper() == 'SELECT':
            return True
    return False

def extract_from_part(parsed):
    from_seen = False
    for item in parsed.tokens:
        if from_seen:
            if is_subselect(item):
                for x in extract_from_part(item):
                    yield x
            else:
                yield item
        elif item.ttype is Keyword and item.value.upper() == 'FROM':
            from_seen = True

"""
    Purpose: Get all the table identifiers
    Return: Array with identifiers
"""
def extract_table_identifiers(token_stream):
    for item in token_stream:
        if isinstance(item, IdentifierList):
            for identifier in item.get_identifiers():
                yield identifier.get_name()
        elif isinstance(item, Identifier):
            yield item.get_name()
        # It's a bug to check for Keyword here, but in the example
        # above some tables names are identified as keywords...
        elif item.ttype is Keyword:
            yield item.value

"""
    Purpose: Get all the table names where the SQL is searching
    Return: List with the table names
"""
def extract_tables(query):
    stream = extract_from_part(sqlparse.parse(query)[0])
    return list(extract_table_identifiers(stream))

"""
    Purpose: Normalize the column names from tuple to string
    Return: Array of string with the column names
"""
def normalizeColumnNames(columnNames):
    normalizedColumnNames = []
    for columnName in columnNames:
        columnName = columnName[0]

        normalizedColumnNames.append(columnName)

    return normalizedColumnNames

"""
    Purpose: Check if the query is used just to select data
    Return: Boolean, where True means valid query and False invalid query
"""
def verifyQuery(query):
    query = str(query.lower())
    sqlActionsNotAllowed = ('insert', 'drop', 'delete', 'update', 'create')

    if not ("select" in query):
        return False

    for action in sqlActionsNotAllowed:
        if (action in query):
            return False

    return True

"""
    Purpose: Check if a database connection can be done (MySQL)
    Return: Boolean, where True means success and False fail
"""
def testDbConnection(host, port, user, passwd, db):
    try:
        db = MySQLdb.connect(host=host,port=int(port), user=user,passwd=passwd,db=db)
        cursor = db.cursor()
        cursor.execute("SELECT VERSION()")
        results = cursor.fetchone()

        return True
    except Exception, e:
        return False
