from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import *
from django.core.urlresolvers import *
from django.views import *
from django.db import connection
from django.views.generic import TemplateView

from .forms import *

import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

import MySQLdb

from django.contrib import messages
from .models import *

def dashboard(request):
    return render(request, 'database_manager/dashboard.html', {})

def db_connection_run_queries(request, db_connection_id):
    dbConnection = get_object_or_404(DatabaseConnection, pk=db_connection_id)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = QuerySearch(request.POST)
        # check whether it's valid:
        if form.is_valid():
            query = form.cleaned_data['query']

            data = {
                'query': query
            }
            form = QuerySearch(data)

            if verifyQuery(query) == False:
                messages.error(request, "The Sql Query is not permitted, please enter a Sql Query valid")

                return render(
                    request,
                    'database_manager/db_connection_run_querie.html',
                    {
                        'queryResult': None,
                        'headers': None,
                        'search_query_form': form,
                        'db_connection_id': db_connection_id
                    }
                )

            db = dbConnection.databaseName
            host = dbConnection.hostName
            port = dbConnection.port
            user = dbConnection.username
            passwd = dbConnection.password

            try:
                # We execute the query
                db = MySQLdb.connect(host=host, port=int(port), user=user,passwd=passwd,db=db)
                cursor = db.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()

                # We obtain the column names to display as headers in table
                headers = parseSQL(query, cursor)

                messages.success(request, "Query executed!")
            except Exception, e:
                rows = None
                headers = None

                messages.error(request, "The Sql Query is not permitted, please enter a Sql Query validS")

            # tables = extract_tables(query)

            return render(
                request,
                'database_manager/db_connection_run_querie.html',
                {
                    'queryResult': rows,
                    'headers': headers,
                    'search_query_form': form,
                    'db_connection_id': db_connection_id
                }
            )

    else:
        form = QuerySearch()

    return render(
        request,
        'database_manager/db_connection_run_querie.html',
        {
            'search_query_form': form,
            'db_connection_id': db_connection_id
        }
    )

def db_connection_list(request):
    dbConnections = DatabaseConnection.objects.all()
    return render(request, 'database_manager/db_connection_list.html', {'database_connections':dbConnections})

def db_connection_add(request):
    if request.method == 'POST':

        form = DatabaseConnectionForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            databaseName = form.cleaned_data['databaseName']
            hostName = form.cleaned_data['hostName']
            port = form.cleaned_data['port']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if (testDbConnection(hostName, port, username, password, databaseName) == False):
                messages.error(request, "Connection failed")
                return render(request, 'database_manager/db_connection_add.html', {'add_connection_form': form, 'error_message':'bad connection'})

            try:
                dbConnection = DatabaseConnection(
                    name= name,
                    databaseName= databaseName,
                    hostName= hostName,
                    port= port,
                    username= username,
                    password= password
                )

                dbConnection.save()

                form = DatabaseConnectionForm()
                messages.success(request, "Connection Created")
            except Exception, e:
                messages.error(request, "Invalid data")

            return render(request, 'database_manager/db_connection_add.html', {'add_connection_form': form})

    else:
        form = DatabaseConnectionForm()

    return render(request, 'database_manager/db_connection_add.html', {'add_connection_form': form, 'error_message':'nuevo'})

def db_connection_edit(request, db_connection_id):
    dbConnection = get_object_or_404(DatabaseConnection, pk=db_connection_id)
    if request.method == 'POST':

        form = DatabaseConnectionEditForm(request.POST, instance=dbConnection)

        if form.is_valid():
            databaseName = form.cleaned_data['databaseName']
            hostName = form.cleaned_data['hostName']
            port = form.cleaned_data['port']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if (testDbConnection(hostName, port, username, password, databaseName) == False):
                messages.error(request, "Connection failed")

                return render(
                    request,
                    'database_manager/db_connection_edit.html',
                    {
                        'edit_connection_form': form,
                        'db_connection': dbConnection
                    }
                )

            try:
                form.save()
                messages.success(request, "Connection Edited")
            except Exception, e:
                messages.error(request, "Invalid data")

        dbConnections = DatabaseConnection.objects.all()
        return render(request, 'database_manager/db_connection_list.html', {'database_connections':dbConnections})

    else:
        form = DatabaseConnectionEditForm(instance=dbConnection)

    return render(
        request,
        'database_manager/db_connection_edit.html',
        {
            'edit_connection_form': form,
            'db_connection': dbConnection
        }
    )

def db_connection_delete(request, db_connection_id):
    dbConnections = DatabaseConnection.objects.all()
    try:
        dbConnection = get_object_or_404(DatabaseConnection, pk=db_connection_id)
        dbConnection.delete()
        messages.success(request, "Connection deleted")
    except Exception, e:
        messages.error(request, "Connection not deleted")

    return render(request, 'database_manager/db_connection_list.html', {'database_connections':dbConnections})

####################### Functions #############################

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
        if ("u'" in columnName or "('" in columnName):
            columnName = find_between(columnName, "'", "'")

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
