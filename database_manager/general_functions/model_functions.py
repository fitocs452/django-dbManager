# Django imports
from django.shortcuts import render, get_object_or_404

# Custom file imports
from database_manager.models import *

def getDatabaseConnectionsByUser(user_id):
    db_connections = DatabaseConnection.objects.filter(user_id = user_id)

    return db_connections

def getDatabaseQueriesByDatabase(db_connection_id):
    db_connection = get_object_or_404(DatabaseConnection, pk = db_connection_id)

    return DatabaseQuery.objects.filter(database_connection = db_connection)
