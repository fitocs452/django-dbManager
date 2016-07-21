from django.conf.urls import url

from . import views

app_name = "users_administrator"
urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^users$', views.AdminDashboardView.as_view(), name='users_list'),
]
