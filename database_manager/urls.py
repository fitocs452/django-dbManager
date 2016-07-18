from django.conf.urls import url

from . import views

app_name = "database_manager"
urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^db_connections/(?P<db_connection_id>[0-9]+)/run_querie$', views.db_connection_run_queries, name='db_run_querie'),
    url(r'^db_connections/$', views.db_connection_list, name='db_connections_list'),
    url(r'^db_connections/add/$', views.db_connection_add, name='db_connections_add'),
    url(r'^db_connections/(?P<db_connection_id>[0-9]+)/edit/$', views.db_connection_edit, name='db_connection_edit'),
    url(r'^db_connections/(?P<db_connection_id>[0-9]+)/delete/$', views.db_connection_delete, name='db_connections_delete'),
    url(r'^db_connections/(?P<db_connection_id>[0-9]+)/db_query/new$', views.db_query_save, name='db_query_add'),
    url(r'^db_connections/(?P<db_connection_id>[0-9]+)/run_querie/(?P<db_query_id>[0-9]+)$', views.db_connection_run_query, name='db_run_query_listed')
]
