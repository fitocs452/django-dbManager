from django import forms
from .models import DatabaseConnection, DatabaseQuery

class QuerySearch(forms.Form):
    query = forms.CharField(max_length = 250, widget = forms.Textarea, required = True)

class DatabaseConnectionModelForm(forms.ModelForm):
    class Meta:
        model = DatabaseConnection
        fields = ['name', 'databaseName', 'hostName', 'port', 'username', 'password']

class DatabaseQueryModelForm(forms.ModelForm):
    class Meta:
        model = DatabaseQuery
        fields = ['name', 'database_connection', 'query']
        exclude = ('database_connection',)
