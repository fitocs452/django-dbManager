from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.test import Client

from .models import *
from .views import *
from .forms import *

class DatabaseConnectionTests(TestCase):

    def test_database_connection_list(self):
        """
            Test the list of database connection.
            For example:
                If I create a new DatabaseConnection,
                it should appear in the database connection list
        """
        mongoType = DatabaseType(db_type = 'Mongo')
        mongoType.save()
        mysqlType = DatabaseType(db_type = 'MySQL')
        mysqlType.save()
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        DatabaseConnection.objects.create(type = mysqlType, name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 33016, username = 'root', password = 'admin', user_id = user.id)
        DatabaseConnection.objects.create(type = mongoType, name = 'Test2', databaseName = 'local', hostName = 'localhost', port = 27017, username = 'root', password = 'viaro', user_id = user.id)

        response = self.client.get(reverse('database_manager:db_connections_list'))

        self.assertQuerysetEqual(
            response.context['database_connections'].order_by('name'),
            ['<DatabaseConnection: Test1>', '<DatabaseConnection: Test2>']
        )

    def test_add_database_connection_success(self):
        """
            Test the database connection creation via form
            Purpose: (Success Test - The connection is saved)
            Test:
                - Verify if the form validations are working
                - Verify if the connection is succesful, if not it wont be saved
                - If is created successfully then it will appear on the database connection list
        """
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

        mongoType = DatabaseType(db_type = 'Mongo')
        mongoType.save()
        mysqlType = DatabaseType(db_type = 'MySQL')
        mysqlType.save()

        response_post = self.client.post(
            reverse('database_manager:db_connections_add'),
            data = {
                'type': mysqlType.id,
                'name': 'Test',
                'databaseName': 'dbmanager_test',
                'collection': 'None',
                'hostName': 'localhost',
                'port': '3306',
                'username': 'root',
                'password': 'viaro',
            }
        )
        self.assertRedirects(response_post, reverse('database_manager:db_connections_list'))

        response_post = self.client.post(
            reverse('database_manager:db_connections_add'),
            data = {
                'type': mongoType.id,
                'name': 'Test_Mongo',
                'databaseName': 'local',
                'collection': 'TestMongo',
                'hostName': 'localhost',
                'port': '27017',
                'username': 'root',
                'password': 'viaro',
            }
        )
        self.assertRedirects(response_post, reverse('database_manager:db_connections_list'))

        response_get = self.client.get(reverse('database_manager:db_connections_list'))
        self.assertQuerysetEqual(
            response_get.context['database_connections'].order_by('name'),
            ['<DatabaseConnection: Test>', '<DatabaseConnection: Test_Mongo>']
        )

    def test_add_database_connection_fail(self):
        """
            Test the database connection creation via form
            Purpose: (Fail Test - The connection isn't saved)
            Test:
                - Verify if the form validations are working
                - Verify if the connection is succesful, if not it wont be saved
        """
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

        mysqlType = DatabaseType(db_type = 'MySQL')
        mysqlType.save()

        response_post = self.client.post(
            reverse('database_manager:db_connections_add'),
            data = {
                'type': mysqlType.id,
                'name': 'Test',
                'databaseName': 'dbmanager_test',
                'hostName': 'localhost',
                'collection': 'None',
                'port': '33060',
                'username': 'root',
                'password': 'admin',
            }
        )

        self.assertIn('Connection failed', str(response_post.content))

    def test_edit_database_connection_success(self):
        """
            Test the database connection edit function via form
            Purpose: (Success Test - The connection changes are saved)
            Test:
                - Verify if the form validations are working
                - Verify if the connection is succesful, if not it wont be saved
                - If is created successfully then it will appear on the database connection list
        """

        mysqlType = DatabaseType(db_type = 'MySQL')
        mysqlType.save()
        mongoType = DatabaseType(db_type = 'Mongo')
        mongoType.save()

        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        db = DatabaseConnection.objects.create(type = mysqlType, name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 3306, username = 'root', password = 'viaro', user_id = user.id)
        db_2 = DatabaseConnection.objects.create(type = mongoType, name = 'Test2', databaseName = 'local', hostName = 'localhost', port = 27017, username = 'root', password = 'viaro', user_id = user.id)

        response_post = self.client.post(
            reverse('database_manager:db_connection_edit', kwargs = { 'db_connection_id' : db.id }),
            data = {
                'type': mysqlType.id,
                'name': 'Test_1',
                'databaseName': 'dbmanager_test',
                'hostName': 'localhost',
                'collection': 'None',
                'port': '3306',
                'username': 'root',
                'password': 'viaro',
            }
        )

        response_post = self.client.post(
            reverse('database_manager:db_connection_edit', kwargs = { 'db_connection_id' : db_2.id }),
            data = {
                'type': mongoType.id,
                'name': 'Test_2',
                'databaseName': 'dbmanager_test',
                'hostName': 'localhost',
                'collection': 'TestMongo',
                'port': '27017',
                'username': 'root',
                'password': 'viaro',
            }
        )

        self.assertRedirects(response_post, reverse('database_manager:db_connections_list'))

        response_get = self.client.get(reverse('database_manager:db_connections_list'))
        self.assertQuerysetEqual(
            response_get.context['database_connections'].order_by('name'),
            ['<DatabaseConnection: Test_1>', '<DatabaseConnection: Test_2>']
        )

    def test_edit_database_connection_fail(self):
        """
            Test the database connection edit function via form
            Purpose: (Fail Test - The connection changes aren't saved)
            Test:
                - Verify if the form validations are working
                - Verify if the connection is succesful, if not it wont be saved
        """
        mysqlType = DatabaseType(db_type = 'MySQL')
        mysqlType.save()
        mongoType = DatabaseType(db_type = 'Mongo')
        mongoType.save()

        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        db = DatabaseConnection.objects.create(type = mysqlType, name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 3306, username = 'root', password = 'viaro', user_id = user.id)
        db_2 = DatabaseConnection.objects.create(type = mongoType, name = 'Test2', databaseName = 'local', hostName = 'localhost', port = 27017, username = 'root', password = 'viaro', user_id = user.id)

        response_post = self.client.post(
            reverse('database_manager:db_connection_edit', kwargs = { 'db_connection_id' : db.id }),
            data = {
                'type': mysqlType.id,
                'name': 'Test_1',
                'databaseName': 'dbmanager_test',
                'hostName': 'localhost',
                'collection': 'None',
                'port': '33016',
                'username': 'root',
                'password': 'admin',
            }
        )

        self.assertIn('Connection failed', str(response_post.content))

        response_post = self.client.post(
            reverse('database_manager:db_connection_edit', kwargs = { 'db_connection_id' : db_2.id }),
            data = {
                'type': mongoType.id,
                'name': 'Test_2',
                'databaseName': 'dbmanager_test',
                'hostName': 'localhost',
                'collection': 'TestMongo2',
                'port': '3306',
                'username': 'root',
                'password': 'viaro',
            }
        )

        self.assertIn('Connection failed', str(response_post.content))

        response_get = self.client.get(reverse('database_manager:db_connections_list'))
        self.assertQuerysetEqual(
            response_get.context['database_connections'].order_by('name'),
            ['<DatabaseConnection: Test1>', '<DatabaseConnection: Test2>']
        )

class DatabaseQueryTests(TestCase):
    def test_add_database_query_success(self):
        """
            Test the database connection creation via form
            Purpose: (Success Test - The database query is saved)
            Test:
                - Verify if the form validations are working
                - Verify if the query is correct, if not it wont be saved
        """
        mysqlType = DatabaseType(db_type = 'MySQL')
        mysqlType.save()
        mongoType = DatabaseType(db_type = 'Mongo')
        mongoType.save()

        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        db = DatabaseConnection.objects.create(type = mysqlType, name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 3306, username = 'root', password = 'admin', user_id = user.id)
        db_2 = DatabaseConnection.objects.create(type = mongoType, name = 'Test2', databaseName = 'local', collection = 'TestMongo',hostName = 'localhost', port = 27017, username = 'root', password = 'viaro', user_id = user.id)

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

        route = reverse('database_manager:db_run_query', kwargs = { 'db_connection_id' : db_2.id })
        response_post = self.client.post(
            reverse('database_manager:db_query_add', kwargs = { 'db_connection_id' : db_2.id }),
            data = {
                'name': 'TestQuery',
                'query': '{"age": {"$gt": 19, "$lt": 35}}'
            }
        )

        self.assertRedirects(response_post, route)

        response_get = self.client.get(route)
        self.assertIn('TestQuery', str(response_get.content))

    def test_add_database_query_fail(self):
        """
            Test the database connection creation via form
            Purpose: (Fail Test - The database query isn't saved)
            Test:
                - Verify if the form validations are working
                - Verify if the query is correct, if not it wont be saved
        """

        mysqlType = DatabaseType(db_type = 'MySQL')
        mysqlType.save()

        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        db = DatabaseConnection.objects.create(type = mysqlType, name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 3306, username = 'root', password = 'viaro', user_id = user.id)

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

    def test_run_query_success(self):
        """
            Test the if a query can be run
            Purpose: (Success Test - The database query is ran)
            Test:
                - Verify if the form validations are working
                - Verify if the SQL is correct, if not it wont be ran
        """
        mysqlType = DatabaseType(db_type = 'MySQL')
        mysqlType.save()
        mongoType = DatabaseType(db_type = 'Mongo')
        mongoType.save()

        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        db = DatabaseConnection.objects.create(type = mysqlType, name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 3306, username = 'root', password = 'viaro', user_id = user.id)
        db_2 = DatabaseConnection.objects.create(type = mongoType, name = 'Test2', databaseName = 'local', collection = 'TestMongo', hostName = 'localhost', port = 27017, username = 'root', password = 'viaro', user_id = user.id)

        route = reverse('database_manager:db_run_query', kwargs = { 'db_connection_id' : db.id })
        response_post = self.client.post(
            route,
            data = {
                'query': "select * from random_name;"
            }
        )

        self.assertIn('adolfo', str(response_post.content))

        route = reverse('database_manager:db_run_query', kwargs = { 'db_connection_id' : db_2.id })
        response_post = self.client.post(
            route,
            data = {
                'query': '{ "age": { "$gt": 19, "$lt": 35 }, "name": "Habiba" }'
            }
        )

        self.assertIn('Habiba', str(response_post.content))

    def test_run_query_fail(self):
        """
            Test the if a query can be run
            Purpose: (Fail Test - The database query isn't ran)
            Test:
                - Verify if the form validations are working
                - Verify if the SQL is correct, if not it wont be ran
        """
        mysqlType = DatabaseType(db_type = 'MySQL')
        mysqlType.save()
        mongoType = DatabaseType(db_type = 'Mongo')
        mongoType.save()

        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')
        db = DatabaseConnection.objects.create(type = mysqlType, name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 3306, username = 'root', password = 'viaro', user_id = user.id)
        db_2 = DatabaseConnection.objects.create(type = mongoType, name = 'Test2', databaseName = 'local', collection = 'TestMongo', hostName = 'localhost', port = 27017, username = 'root', password = 'viaro', user_id = user.id)

        route = reverse('database_manager:db_run_query', kwargs = { 'db_connection_id' : db.id })
        response_post = self.client.post(
            route,
            data = {
                'query': "select * from nonexistent_table;"
            }
        )

        self.assertIn('The Sql Query is not permitted, please enter a Sql Query', str(response_post.content))
        self.assertNotIn('adolfo', str(response_post.content))

        route = reverse('database_manager:db_run_query', kwargs = { 'db_connection_id' : db_2.id })
        response_post = self.client.post(
            route,
            data = {
                'query': "select * from nonexistent_table;"
            }
        )

        self.assertIn('The Sql Query is not permitted, please enter a Sql Query', str(response_post.content))
        self.assertNotIn('adolfo', str(response_post.content))

