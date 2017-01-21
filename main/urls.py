from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^submit/$', views.submit, name='submit'),
    url(r'^show/$', views.show),
    url(r'^show/(.+)/(.+)$', views.method),
    url(r'^plot/', views.plot),
]