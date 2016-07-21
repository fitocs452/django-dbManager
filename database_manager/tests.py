from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.test import Client

from .models import *
from .views import *
from .forms import *

class DatabaseConnectionTests(TestCase):

    """
        Test the list of database connection.
        For example:
            If I create a new DatabaseConnection,
            it should appear in the database connection list
    """
    def test_database_connection_list(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        DatabaseConnection.objects.create(name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 33016, username = 'root', password = 'admin', user_id = user.id)
        DatabaseConnection.objects.create(name = 'Test2', databaseName = 'dbmanager_test', hostName = 'localhost', port = 33016, username = 'root', password = 'admin', user_id = user.id)
        response = self.client.get(reverse('database_manager:db_connections_list'))

        self.assertQuerysetEqual(
            response.context['database_connections'].order_by('name'),
            ['<DatabaseConnection: Test1>', '<DatabaseConnection: Test2>']
        )

    """
        Test the database connection creation via form
        Purpose: (Success Test - The connection is saved)
        Test:
            - Verify if the form validations are working
            - Verify if the connection is succesful, if not it wont be saved
            - If is created successfully then it will appear on the database connection list
    """
    def test_add_database_connection_success(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

        response_post = self.client.post(
            reverse('database_manager:db_connections_add'),
            data = {
                'name': 'Test',
                'databaseName': 'dbmanager_test',
                'hostName': 'localhost',
                'port': '3306',
                'username': 'root',
                'password': 'viaro',
            }
        )

        self.assertRedirects(response_post, reverse('database_manager:db_connections_list'))

        response_get = self.client.get(reverse('database_manager:db_connections_list'))
        self.assertQuerysetEqual(
            response_get.context['database_connections'].order_by('name'),
            ['<DatabaseConnection: Test>']
        )

    """
        Test the database connection creation via form
        Purpose: (Fail Test - The connection isn't saved)
        Test:
            - Verify if the form validations are working
            - Verify if the connection is succesful, if not it wont be saved
    """
    def test_add_database_connection_fail(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

        response_post = self.client.post(
            reverse('database_manager:db_connections_add'),
            data = {
                'name': 'Test',
                'databaseName': 'dbmanager_test',
                'hostName': 'localhost',
                'port': '33016',
                'username': 'root',
                'password': 'admin',
            }
        )

        self.assertIn('Connection failed', str(response_post.content))

    """
        Test the database connection edit function via form
        Purpose: (Success Test - The connection changes are saved)
        Test:
            - Verify if the form validations are working
            - Verify if the connection is succesful, if not it wont be saved
            - If is created successfully then it will appear on the database connection list
    """
    def test_edit_database_connection_success(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        db = DatabaseConnection.objects.create(name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 3306, username = 'root', password = 'admin', user_id = user.id)

        response_post = self.client.post(
            reverse('database_manager:db_connection_edit', kwargs = { 'db_connection_id' : db.id }),
            data = {
                'name': 'Test_1',
                'databaseName': 'dbmanager_test',
                'hostName': 'localhost',
                'port': '3306',
                'username': 'root',
                'password': 'viaro',
            }
        )

        self.assertRedirects(response_post, reverse('database_manager:db_connections_list'))

        response_get = self.client.get(reverse('database_manager:db_connections_list'))
        self.assertQuerysetEqual(
            response_get.context['database_connections'].order_by('name'),
            ['<DatabaseConnection: Test_1>']
        )

    """
        Test the database connection edit function via form
        Purpose: (Fail Test - The connection changes aren't saved)
        Test:
            - Verify if the form validations are working
            - Verify if the connection is succesful, if not it wont be saved
    """
    def test_edit_database_connection_fail(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        db = DatabaseConnection.objects.create(name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 33016, username = 'root', password = 'admin', user_id = user.id)

        response_post = self.client.post(
            reverse('database_manager:db_connection_edit', kwargs = { 'db_connection_id' : db.id }),
            data = {
                'name': 'Test_1',
                'databaseName': 'dbmanager_test',
                'hostName': 'localhost',
                'port': '33016',
                'username': 'root',
                'password': 'admin',
            }
        )

        self.assertIn('Connection failed', str(response_post.content))

        response_get = self.client.get(reverse('database_manager:db_connections_list'))
        self.assertQuerysetEqual(
            response_get.context['database_connections'].order_by('name'),
            ['<DatabaseConnection: Test1>']
        )

class DatabaseQueryTests(TestCase):
    """
        Test the database connection creation via form
        Purpose: (Success Test - The database query is saved)
        Test:
            - Verify if the form validations are working
            - Verify if the query is correct, if not it wont be saved
    """
    def test_add_database_query_success(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        db = DatabaseConnection.objects.create(name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 3306, username = 'root', password = 'admin', user_id = user.id)

        route = reverse('database_manager:db_run_query', kwargs = { 'db_connection_id' : db.id })
        response_post = self.client.post(
            reverse('database_manager:db_query_add', kwargs = { 'db_connection_id' : db.id }),
            data = {
                'name': 'TestQuery',
                'query': 'Select * from random_name;'
            }
        )

        self.assertRedirects(response_post, route)

        response_get = self.client.get(route)
        self.assertIn('TestQuery', str(response_get.content))

    """
        Test the database connection creation via form
        Purpose: (Fail Test - The database query isn't saved)
        Test:
            - Verify if the form validations are working
            - Verify if the query is correct, if not it wont be saved
    """
    def test_add_database_query_fail(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        db = DatabaseConnection.objects.create(name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 3306, username = 'root', password = 'viaro', user_id = user.id)

        route = reverse('database_manager:db_query_add', kwargs = { 'db_connection_id' : db.id })
        response_post = self.client.post(
            route,
            data = {
                'name': 'TestQuery',
                'query': "insert into random_names values(1, 'test')"
            }
        )

        self.assertIn('The Sql Query is not permitted, please enter a Sql Query', str(response_post.content))

        response_get = self.client.get(reverse('database_manager:db_run_query', kwargs = { 'db_connection_id' : db.id }))
        self.assertNotIn('TestQuery', str(response_get.content))

    """
        Test the if a query can be run
        Purpose: (Success Test - The database query is ran)
        Test:
            - Verify if the form validations are working
            - Verify if the SQL is correct, if not it wont be ran
    """
    def test_run_query_success(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        db = DatabaseConnection.objects.create(name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 3306, username = 'root', password = 'viaro', user_id = user.id)

        route = reverse('database_manager:db_run_query', kwargs = { 'db_connection_id' : db.id })
        response_post = self.client.post(
            route,
            data = {
                'query': "select * from random_name;"
            }
        )

        self.assertIn('adolfo', str(response_post.content))

    """
        Test the if a query can be run
        Purpose: (Fail Test - The database query isn't ran)
        Test:
            - Verify if the form validations are working
            - Verify if the SQL is correct, if not it wont be ran
    """
    def test_run_query_success(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        db = DatabaseConnection.objects.create(name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 3306, username = 'root', password = 'viaro', user_id = user.id)

        route = reverse('database_manager:db_run_query', kwargs = { 'db_connection_id' : db.id })
        response_post = self.client.post(
            route,
            data = {
                'query': "select * from nonexistent_table;"
            }
        )

        self.assertIn('The Sql Query is not permitted, please enter a Sql Query', str(response_post.content))
        self.assertNotIn('adolfo', str(response_post.content))

