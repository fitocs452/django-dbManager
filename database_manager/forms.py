from django import forms
from .models import DatabaseConnection, DatabaseQuery, DatabaseType

class QuerySearch(forms.Form):
    query = forms.CharField(max_length = 250, widget = forms.Textarea, required = True)

class DatabaseConnectionModelForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = DatabaseConnection
        fields = ['type', 'name', 'databaseName', 'hostName', 'port', 'username', 'password']

    def __init__(self, *args, **kwargs):
        super(DatabaseConnectionModelForm, self).__init__(*args, **kwargs)
        self.fields['type'].queryset = DatabaseType.objects.all()

class DatabaseQueryModelForm(forms.ModelForm):
    class Meta:
        model = DatabaseQuery
        fields = ['name', 'database_connection', 'query']
        exclude = ('database_connection',)
