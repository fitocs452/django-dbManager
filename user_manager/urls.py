from django.conf.urls import url

from . import views

app_name = "user_manager"
urlpatterns = [
    url(r'^$', views.register, name='register'),
    url(r'^$', views.lgoin, name='login'),
]
