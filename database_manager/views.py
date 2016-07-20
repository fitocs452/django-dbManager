# Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import *
from django.core.urlresolvers import *
from django.views import *
from django.db import connection
from django.views.generic import TemplateView, View
from django.contrib import messages

# Third party imports
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

import MySQLdb

# Custom file imports
from .models import *
from .forms import *

from .general_functions.db_connection_functions import *
from .general_functions.model_functions import *

def dashboard(request):
    return render(request, 'database_manager/dashboard.html', {})

class DatabaseConnectionCreateView(View):
    def get(self, request):
        form = DatabaseConnectionModelForm()

        return render(
            request,
            'database_manager/db_connection_add.html',
            {
                'add_connection_form': form
            }
        )

    def post(self, request):
        form = DatabaseConnectionModelForm(request.POST)

        if form.is_valid():
            databaseName = form.cleaned_data['databaseName']
            hostName = form.cleaned_data['hostName']
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            port = form.cleaned_data['port']
            username = form.cleaned_data['username']

            if (not testDbConnection(hostName, port, username, password, databaseName)):
                messages.error(request, "Connection failed")

                return render(request, 'database_manager/db_connection_add.html', {'add_connection_form': form})

            dbConnection = DatabaseConnection(
                name = name,
                databaseName = databaseName,
                hostName = hostName,
                port = port,
                username = username,
                password = password,
                user_id = request.user.id       # We obtain the user logged
            )

            dbConnection.save()

            form = DatabaseConnectionForm()
            messages.success(request, "Connection Created")

        return redirect('/database_manager/db_connections/')

class DatabaseConnectionEditView(View):
    def get(self, request, db_connection_id):
        dbConnection = get_object_or_404(DatabaseConnection, pk = db_connection_id)
        form = DatabaseConnectionModelForm(instance = dbConnection)

        return render(
            request,
            'database_manager/db_connection_edit.html',
            {
                'edit_connection_form': form,
                'db_connection': dbConnection
            }
        )

    def post(self, request, db_connection_id):
        dbConnection = get_object_or_404(DatabaseConnection, pk = db_connection_id)
        form = DatabaseConnectionModelForm(request.POST, instance = dbConnection)

        if form.is_valid():
            databaseName = form.cleaned_data['databaseName']
            hostName = form.cleaned_data['hostName']
            port = form.cleaned_data['port']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if (not testDbConnection(hostName, port, username, password, databaseName)):
                messages.error(request, "Connection failed")

                return render(
                    request,
                    'database_manager/db_connection_edit.html',
                    {
                        'edit_connection_form': form,
                        'db_connection': dbConnection
                    }
                )

            form.save()
            messages.success(request, "Connection Edited")

        return redirect('/database_manager/db_connections/')

class DatabaseQueryCreateView(View):
    def get(self, request, db_connection_id):
        dbConnection = get_object_or_404(DatabaseConnection, pk = db_connection_id)
        dbQuery = DatabaseQuery(database_connection = dbConnection)
        form = DatabaseQueryModelForm(instance = dbQuery)

        return render(
            request,
            'database_manager/db_query_add.html',
            {
                'add_query_form': form,
                'db_connection_id':db_connection_id
            }
        )

    def post(self, request, db_connection_id):
        form = DatabaseQueryModelForm(request.POST)
        redirectUrl = "/database_manager/db_connections/%d/run_query" % (int(db_connection_id))

        if form.is_valid():
            name = form.cleaned_data['name']
            query = form.cleaned_data['query']

            dbConnection = get_object_or_404(DatabaseConnection, pk = db_connection_id)

            dbQuery = DatabaseQuery(
                name = name,
                query = query,
                database_connection = dbConnection
            )

            dbQuery.save()
            form = DatabaseQueryModelForm()
            messages.success(request, "Query Saved")

        return redirect(redirectUrl)

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

                queries_saved_list = DatabaseQuery.objects.filter(database_connection = dbConnection)

                return render(
                    request,
                    'database_manager/db_connection_run_querie.html',
                    {
                        'queryResult': None,
                        'headers': None,
                        'search_query_form': form,
                        'db_connection_id': db_connection_id,
                        'queries_list': queries_saved_list
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

                messages.error(request, "The Sql Query is not permitted, please enter a Sql Query valid")

            # tables = extract_tables(query)

            queries_saved_list = DatabaseQuery.objects.filter(database_connection = dbConnection)

            return render(
                request,
                'database_manager/db_connection_run_querie.html',
                {
                    'queryResult': rows,
                    'headers': headers,
                    'search_query_form': form,
                    'db_connection_id': db_connection_id,
                    'queries_list': queries_saved_list
                }
            )

    else:
        form = QuerySearch()

    queries_saved_list = DatabaseQuery.objects.filter(database_connection = dbConnection)

    return render(
        request,
        'database_manager/db_connection_run_querie.html',
        {
            'search_query_form': form,
            'db_connection_id': db_connection_id,
            'queries_list': queries_saved_list
        }
    )

def db_connection_list(request):
    logged_user = request.user
    dbConnections = getDatabaseConnectionsByUser(logged_user)
    return render(request, 'database_manager/db_connection_list.html', {'database_connections':dbConnections})

def db_connection_delete(request, db_connection_id):
    try:
        dbConnection = get_object_or_404(DatabaseConnection, pk=db_connection_id)
        dbConnection.delete()
        messages.success(request, "Connection deleted")
    except Exception, e:
        messages.error(request, "Connection not deleted")

    dbConnections = DatabaseConnection.objects.all()
    return render(request, 'database_manager/db_connection_list.html', {'database_connections':dbConnections})

def db_connection_run_query(request, db_connection_id, db_query_id):
    dbConnection = get_object_or_404(DatabaseConnection, pk=db_connection_id)
    dbQuery = get_object_or_404(DatabaseQuery, pk = db_query_id)

    query = dbQuery.query
    db = dbConnection.databaseName
    host = dbConnection.hostName
    port = dbConnection.port
    user = dbConnection.username
    passwd = dbConnection.password

    # We execute the query
    db = MySQLdb.connect(host=host, port=int(port), user=user,passwd=passwd,db=db)
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    # We obtain the column names to display as headers in table
    headers = parseSQL(query, cursor)

    messages.success(request, "Query executed!")

    # tables = extract_tables(query)
    form = QuerySearch(initial = { 'query': query})
    queries_saved_list = DatabaseQuery.objects.filter(database_connection = dbConnection)

    return render(
        request,
        'database_manager/db_connection_run_querie.html',
        {
            'queryResult': rows,
            'headers': headers,
            'search_query_form': form,
            'db_connection_id': db_connection_id,
            'queries_list': queries_saved_list
        }
    )
