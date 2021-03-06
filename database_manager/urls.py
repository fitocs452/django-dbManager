from django.conf.urls import url

from . import views

app_name = "database_manager"
urlpatterns = [
    url(r'^$', views.DashboardView.as_view(), name='dashboard'),
    url(r'^db_connections/(?P<db_connection_id>[0-9]+)/run_query$', views.DatabaseRunQuery.as_view(), name='db_run_query'),
    url(r'^db_connections/$', views.DatabaseConnectionListView.as_view(), name='db_connections_list'),
    url(r'^db_connections/add/$', views.DatabaseConnectionCreateView.as_view(), name='db_connections_add'),
    url(r'^db_connections/(?P<db_connection_id>[0-9]+)/edit/$', views.DatabaseConnectionEditView.as_view(), name='db_connection_edit'),
    url(r'^db_connections/(?P<db_connection_id>[0-9]+)/delete/$', views.DatabaseConnectionDeleteView.as_view(), name='db_connections_delete'),
    url(r'^db_connections/(?P<db_connection_id>[0-9]+)/db_query/new$', views.DatabaseQueryCreateView.as_view(), name='db_query_add'),
    url(r'^db_connections/(?P<db_connection_id>[0-9]+)/run_query/(?P<db_query_id>[0-9]+)$', views.DatabaseRunQueryListed.as_view(), name='db_run_query_listed')
]
