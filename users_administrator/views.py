# Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.template import *
from django.core.urlresolvers import *
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth.models import User

# Admin Dahsboard
def dashboard(request):
    return render(request, 'users_administrator/dashboard.html', {})

# Here we're gonna list all the users
class AdminDashboardView(View):
    def get(self, request):
        users = User.objects.filter(groups__name__in = ['simple_user'])

        return render(
            request,
            'users_administrator/users_list.html',
            {
                'users' : users
            }
        )


