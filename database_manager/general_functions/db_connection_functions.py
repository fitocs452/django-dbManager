import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

import MySQLdb

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

def extract_tables(query):
    stream = extract_from_part(sqlparse.parse(query)[0])
    return list(extract_table_identifiers(stream))

def normalizeColumnNames(columnNames):
    normalizedColumnNames = []
    for columnName in columnNames:
        # here we cast the tuple to string (if is a tuple)
        columnName = str(columnName)
        # we evaluate is a tuple
        if ("u'" in columnName):
            columnName = find_between(columnName, "u'", "'")

        # this is the base case
        normalizedColumnNames.append(columnName)

    return normalizedColumnNames

# Restriction to use sql only to select
def verifyQuery(query):
    query = str(query.lower())
    sqlActionsNotAllowed = ['insert', 'drop', 'delete', 'update', 'create']

    if ("select" in query) == False:
        return False

    for action in sqlActionsNotAllowed:
        if (action in query) == True:
            return False

    return True

def testDbConnection(host, port, user, passwd, db):
    try:
        db = MySQLdb.connect(host=host,port=int(port), user=user,passwd=passwd,db=db)
        cursor = db.cursor()
        cursor.execute("SELECT VERSION()")
        results = cursor.fetchone()

        return True
    except Exception, e:
        return False
