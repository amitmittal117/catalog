from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index.as_view(), name='ca-portal-login'),
    url(r'^populate/', views.populate.as_view(), name='populate'),
    url(r'^dataextract/', views.dataextract.as_view(), name='dataextract'),
]
