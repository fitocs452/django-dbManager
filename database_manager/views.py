# Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.template import *
from django.core.urlresolvers import *
from django.views.generic import View
from django.contrib import messages

# Custom file imports
from .models import *
from .forms import *

from .general_functions.db_connection_functions import *
from .general_functions.model_functions import *

class DashboardView(View):
    def get(self, request):
        """
            Here we list all the actions that can be done by user
        """
        return render(request, 'database_manager/dashboard.html')

class DatabaseConnectionCreateView(View):
    def get(self, request):
        """
            We show an empty form asking the user the necessary data to
            create a database connection
        """
        form = DatabaseConnectionModelForm()

        return render(
            request,
            'database_manager/db_connection_add.html',
            {
                'add_connection_form': form
            }
        )

    def post(self, request):
        """
            Here we check if the information is correct:
                - Every file data is in correct format (string, number ...)
                - If the connection data is correct (We test the connection)
            And if the data is correct, we create the db connection and
                redirect the user to the list
        """
        form = DatabaseConnectionModelForm(request.POST)    # Handle the form with the request.Post data

        # We check if the form fields data is in correct format
        if form.is_valid():
            print "Data valida"
            # We obtain the data from form
            databaseName = form.cleaned_data['databaseName']
            collection = form.cleaned_data['collection']
            hostName = form.cleaned_data['hostName']
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            port = form.cleaned_data['port']
            username = form.cleaned_data['username']
            dbType = form.cleaned_data['type']

            # Here we check if the connection can be done
            if (not testDbConnection(dbType.db_type, hostName, port, username, password, databaseName, collection)):
                print "Conexion fallida"
                messages.error(request, "Connection failed ")

                return render(request, 'database_manager/db_connection_add.html', {'add_connection_form': form})

            # We create the connection
            dbConnection = DatabaseConnection(
                type = dbType,
                name = name,
                databaseName = databaseName,
                collection = collection,
                hostName = hostName,
                port = port,
                username = username,
                password = password,
                user_id = request.user.id       # We obtain the user logged
            )

            dbConnection.save()    # We save the connection
            messages.success(request, "Connection Created")

        return redirect('/database_manager/db_connections/')

class DatabaseConnectionEditView(View):
    """
        In this view we modify a connection the process is similar to
        the DatabasConnectionCreateView, the difference is that our
        form is handle by an existing object.
    """
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
            collection = form.cleaned_data['collection']
            port = form.cleaned_data['port']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            dbType = form.cleaned_data['type']

            if (not testDbConnection(dbType.db_type, hostName, port, username, password, databaseName, collection)):
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
        """
            We show an empty form asking the user the necessary data to
            create and save a database query
        """
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
        """
            Here we check if the information is correct:
                - Every file data is in correct format (string, number ...)
                - If the query data is correct (We verify the query)
            And if the data is correct, we create the db query and
                redirect the user to the query run url
        """
        form = DatabaseQueryModelForm(request.POST)
        redirectUrl = "/database_manager/db_connections/%d/run_query" % (int(db_connection_id))

        # We verify if the form data is correct
        if form.is_valid():
            name = form.cleaned_data['name']
            query = form.cleaned_data['query']

            # We obtain the datatabase connection
            dbConnection = get_object_or_404(DatabaseConnection, pk = db_connection_id)

            # We check if the query is correct
            if (not verifyQuery(query, dbConnection.type.db_type)):
                messages.error(request, "The Sql Query is not permitted, please enter a Sql Query")
                return render(
                    request,
                    'database_manager/db_query_add.html',
                    {
                        'add_query_form': form,
                        'db_connection_id':db_connection_id
                    }
                )

            # We create the database query
            dbQuery = DatabaseQuery(
                name = name,
                query = query,
                database_connection = dbConnection
            )

            # the database query is saved
            dbQuery.save()
            form = DatabaseQueryModelForm()
            messages.success(request, "Query Saved")

        return redirect(redirectUrl)

class DatabaseRunQuery(View):
    def get(self, request, db_connection_id):
        """
            Here is shown an empty form asking for a query to run and also
            show to the logged user his queries (saved previously)
        """
        dbConnection = get_object_or_404(DatabaseConnection, pk = db_connection_id)
        queries_saved_list = DatabaseQuery.objects.filter(database_connection = dbConnection)
        form = QuerySearch()

        return render(
            request,
            'database_manager/db_connection_run_querie.html',
            {
                'search_query_form': form,
                'db_connection_id': db_connection_id,
                'queries_list': queries_saved_list
            }
        )

    def post(self, request, db_connection_id):
        """
            Here we run a query sent from the query executor
            and if is valid we return the tuples if not we
            return an error message
        """
        redirectUrl = "/database_manager/db_connections/%d/run_query" % (int(db_connection_id))
        dbConnection = get_object_or_404(DatabaseConnection, pk = db_connection_id)
        queries_saved_list = DatabaseQuery.objects.filter(database_connection = dbConnection)

        form = QuerySearch(request.POST)

        # here the form data is checked
        if form.is_valid():
            query = form.cleaned_data['query']

            databaseType = dbConnection.type.db_type

            # The query is verified
            if (not verifyQuery(query, databaseType)):
                messages.error(request, "The SQl Query is not permitted, please enter a Sql Query")
                return redirect(redirectUrl)

            try:
                if (databaseType == 'MySQL'):
                    rows = executeMysqlQuery(dbConnection, query)
                    headers = getHeadersMysql(dbConnection, query)

                if (databaseType == 'Mongo'):
                    rows = executeMongoQuery(dbConnection, query)
                    headers = ['Key', 'Value']

                messages.success(request, "Query executed!")
            except Exception, e:
                rows = None
                headers = None

                messages.error(request, "The Sql Query is not permitted, please enter a Sql Query valid")

        return render(
            request,
            'database_manager/db_connection_run_querie.html',
            {
                'db': databaseType,
                'queryResult': rows,
                'headers': headers,
                'search_query_form': form,
                'db_connection_id': db_connection_id,
                'queries_list': queries_saved_list
            }
        )

class DatabaseConnectionListView(View):
    """
        Here we list all the database connections of the user logged and
        also show him the possible options (Edit, Run Queries and Delete)
    """
    def get(self, request):
        logged_user = request.user
        dbConnections = getDatabaseConnectionsByUser(logged_user)

        return render(request, 'database_manager/db_connection_list.html', {'database_connections':dbConnections})

class DatabaseConnectionDeleteView(View):
    def get(self, request, db_connection_id):
        try:
            dbConnection = get_object_or_404(DatabaseConnection, pk=db_connection_id)
            dbConnection.delete()
            messages.success(request, "Connection deleted")
        except Exception, e:
            messages.error(request, "Connection not deleted")

        return redirect('/database_manager/db_connections/')

class DatabaseRunQueryListed(View):
    def get(self, request, db_connection_id, db_query_id):
        """
            Here is where one of the saved queries of the user logged is ran
        """
        dbConnection = get_object_or_404(DatabaseConnection, pk = db_connection_id)
        dbQuery = get_object_or_404(DatabaseQuery, pk = db_query_id)

        query = dbQuery.query
        databaseType = dbConnection.type.db_type

        if (databaseType == 'MySQL'):
            rows = executeMysqlQuery(dbConnection, query)
            headers = getHeadersMysql(dbConnection, query)

        if (databaseType == 'Mongo'):
            rows = executeMongoQuery(dbConnection, query)
            headers = ['Key', 'Value']

        messages.success(request, "Query executed!")

        # tables = extract_tables(query)
        form = QuerySearch(initial = { 'query': query })
        queries_saved_list = DatabaseQuery.objects.filter(database_connection = dbConnection)

        return render(
            request,
            'database_manager/db_connection_run_querie.html',
            {
                'db': databaseType,
                'queryResult': rows,
                'headers': headers,
                'search_query_form': form,
                'db_connection_id': db_connection_id,
                'queries_list': queries_saved_list
            }
        )
