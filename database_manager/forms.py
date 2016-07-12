from django import forms

class QuerySearch(forms.Form):
    query = forms.CharField(label='Query', max_length=250)

class DatabaseConnection(forms.Form):
    databaseName = forms.CharField(label="Database Name", max_length=50)
    hostName = forms.CharField(label="Hostname", max_length=50)
    port = forms.CharField(label="Port", max_length=50)
    username = forms.CharField(label="Username", max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())
