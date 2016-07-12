from django.conf.urls import url

from . import views

app_name = "database_manager"
urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^queryExecute/$', views.queryExecute, name='queryExecute'),
]
