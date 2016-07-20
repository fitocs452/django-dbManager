from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.test import Client

from .models import *
from .views import *
from .forms import *

class DatabaseConnectionTests(TestCase):

    def test_database_connection_list(self):
        DatabaseConnection.objects.create(name = 'Test1', databaseName = 'dbmanager_test', hostName = 'localhost', port = 33016, username = 'root', password = 'admin')
        DatabaseConnection.objects.create(name = 'Test2', databaseName = 'dbmanager_test', hostName = 'localhost', port = 33016, username = 'root', password = 'admin')
        response = self.client.get(reverse('database_manager:db_connections_list'))

        self.assertQuerysetEqual(
            response.context['database_connections'].order_by('name'),
            ['<DatabaseConnection: Test1>', '<DatabaseConnection: Test2>']
        )

    def test_database_connection_add_view(self):
        response = self.client.get(reverse('database_manager:db_connections_add'))
        self.assertEqual(response.status_code, 200)

    def test_database_connection_add_with_fake_information(self):
        request = 'fake request'
        name = 'world'

        fakeDatabaseConnection = DatabaseConnection.objects.create(
            name = 'Test1',
            databaseName = 'dbmanager_test',
            hostName = 'localhost',
            port = 3306,
            username = 'root',
            password = 'admin'
        )

        form = DatabaseConnectionForm(data={
            'name': 'Test1',
            'databaseName': 'dbmanager_test',
            'hostName': 'localhost',
            'port': 3306,
            'username': 'root',
            'password': 'admin'
        })

        # Validate that form is true
        self.assertTrue(form.is_valid())

        # response = self.client.post('/database_manager/db_connections/add/',
        #     {
        #         'id_name': 'Test1',
        #         'id_databaseName': 'dbmanager_test',
        #         'id_hostName': 'localhost',
        #         'id_port': 3306,
        #         'id_username': 'root',
        #         'id_password': 'admin'
        #     }
        # )

        # has_key = None
        # if (('database_connections' in response.context) == False):
        #     has_key = True

        # print response.context['add_connection_form']

        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(has_key, False)

    def test_database_connection_run_queries_view(self):
        request = 'fake request'
        # resp = self.client.post('/database_manager/db_connections/3/run_querie', {'choice': 1})
        response = db_connection_run_queries(request, 1)
        self.assertEqual(response.status_code, 404)
