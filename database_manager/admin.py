from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

# Register your models here.
from .models import *

class DatabaseQueryInline(admin.TabularInline):
    model = DatabaseQuery
    extra = 1
    # show_change_link = True

class DatabaseConnectionAdmin(admin.ModelAdmin):
    inlines = [DatabaseQueryInline]

class DatabaseConnectionInline(admin.TabularInline):
    fields = ['name', 'databaseName', 'hostName', 'port']
    readonly_fields = fields
    model = DatabaseConnection
    extra = 1
    show_change_link = True

class UserAdmin(AuthUserAdmin):
    inlines = [DatabaseConnectionInline]

class UserAdmin(AuthUserAdmin):
    inlines = [DatabaseConnectionInline]

# unregister old user admin, because we're going to add our custom admin view
admin.site.unregister(User)
# register new user admin
admin.site.register(User, UserAdmin)
admin.site.register(DatabaseConnection, DatabaseConnectionAdmin)
admin.site.register(DatabaseQuery)
