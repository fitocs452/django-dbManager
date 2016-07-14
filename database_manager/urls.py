from django.conf.urls import url

from . import views

app_name = "database_manager"
urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^db_connections/(?P<db_connection_id>[0-9]+)/run_querie$', views.queryExecute, name='db_run_querie'),
    url(r'^db_connections/$', views.listDbConnections, name='db_connections_list'),
    url(r'^db_connections/add/$', views.addDatabaseConnection, name='db_connections_add')
]
