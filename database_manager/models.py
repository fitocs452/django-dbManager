from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords

# Create your models here.

class DatabaseType(models.Model):
    db_type = models.CharField(max_length=15)

    def __str__(self):
        return self.db_type

class DatabaseConnection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    type = models.ForeignKey(DatabaseType, on_delete = models.CASCADE)
    name = models.CharField(max_length=20)
    databaseName = models.CharField(max_length=50)
    collection = models.CharField(max_length=50, default="None")
    hostName = models.CharField(max_length=20)
    port = models.IntegerField(default=3306)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class DatabaseQuery(models.Model):
    name = models.CharField(max_length=20)
    query = models.CharField(max_length=1500)
    database_connection = models.ForeignKey(DatabaseConnection, on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self):
        return self.name
