from __future__ import unicode_literals

from django.db import models

# Create your models here.
class DatabaseConnection(models.Model):
    name = models.CharField(max_length=20)
    databaseName = models.CharField(max_length=50)
    hostName = models.CharField(max_length=20)
    port = models.IntegerField(default=3306)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class DatabaseQuery(models.Model):
    name = models.CharField(max_length=20)
    query = models.CharField(max_length=1500)
    database_connection = models.ForeignKey(DatabaseConnection, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
