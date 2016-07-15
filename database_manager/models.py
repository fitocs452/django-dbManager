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
