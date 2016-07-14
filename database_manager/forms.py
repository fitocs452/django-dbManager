from django import forms

class QuerySearch(forms.Form):
    query = forms.CharField(label='', max_length=250, widget=forms.Textarea, required=True)

class DatabaseConnectionForm(forms.Form):
    name = forms.CharField(label="New Connection Name", max_length=50);
    databaseName = forms.CharField(label="Database Name", max_length=50)
    hostName = forms.CharField(label="Hostname", max_length=50)
    port = forms.CharField(label="Port", max_length=50)
    username = forms.CharField(label="Username", max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())
