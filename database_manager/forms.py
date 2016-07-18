from django import forms
from .models import DatabaseConnection

class QuerySearch(forms.Form):
    query = forms.CharField(label='', max_length=250, widget=forms.Textarea, required=True)

class DatabaseConnectionForm(forms.Form):
    name = forms.CharField(label="New Connection Name", max_length=50);
    databaseName = forms.CharField(label="Database Name", max_length=50)
    hostName = forms.CharField(label="Hostname", max_length=50)
    port = forms.CharField(label="Port", max_length=50)
    username = forms.CharField(label="Username", max_length=50)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

class DatabaseConnectionEditForm(forms.ModelForm):
    class Meta:
        model = DatabaseConnection
        fields = ['name', 'databaseName', 'hostName', 'port', 'username', 'password']

class DatabaseQueryForm(forms.Form):
    name = forms.CharField(label="Querie Name", max_length=20);
    database_connection = forms.CharField(label="Database Connection")
    query = forms.CharField(label="Query", max_length=1500)
