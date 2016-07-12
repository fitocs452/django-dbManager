from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection

from .forms import *
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

def dashboard(request):
    return render(request, 'database_manager/dashboard.html', {})

def queryExecute(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = QuerySearch(request.POST)
        # check whether it's valid:
        if form.is_valid():
            query = form.cleaned_data['query']
            form = QuerySearch()
            error = False

            # try:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            headers = parseSQL(query)
            # except Exception, e:
            #     rows = None
            #     headers = None
            #     error = True


            # tables = extract_tables(query)

            return render(
                request,
                'database_manager/querySearch.html',
                {
                    'queryResult': rows,
                    'headers': headers,
                    'search_query_form': form,
                    'error': error
                    # 'tables': tables
                }
            )

    else:
        form = QuerySearch()

    return render(request, 'database_manager/querySearch.html', {'search_query_form': form})

def addDatabaseConnection(request):
    if request.method == 'POST':
        form = DatabaseConnection(request.POST)

        if form.is_valid():

            return render(request, 'database_manager/dashboard.html', {})

    else:
        form = QuerySearch()

    return render(request, 'database_manager/connections.html', {'add_connection_form': form})

def parseSQL(query):
    query = query.lower()
    # Database connection
    cursor = connection.cursor()

    # Query to select columns from tables (if not defined in select statement)
    columnNameQuery = "SELECT column_name FROM information_schema.columns WHERE table_name='%s'"

    fieldsSelected = find_between(query, 'select', 'from')

    if ('*' in fieldsSelected):
        tables = extract_tables(query)
        fieldsSelected = []
        for table in tables:
            columnsSelectQuery = columnNameQuery % table
            cursor.execute(columnsSelectQuery)
            headers = cursor.fetchall()

            fieldsSelected = fieldsSelected + headers
            fieldsSelected = normalizeColumnNames(fieldsSelected)
        return fieldsSelected
    else:
        fieldsSelected = fieldsSelected.replace(" ", "")
        columns = fieldsSelected.split(',')

        fieldsSelected = []

        for column in columns:
            if ('as' in column):
                index = column.index('as') + 2
                column = column[index:]

            fieldsSelected.append(column)

        return fieldsSelected

####################### Functions #############################

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
        columnName = str(columnName)
        if ("u'" in columnName):
            columnName = find_between(columnName, "u'", "'")

        normalizedColumnNames.append(columnName)

    return normalizedColumnNames
