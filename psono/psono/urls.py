"""psono URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path, include, path
from rest_framework import routers
from django.conf import settings
from restapi import views

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    re_path(r'^', include('restapi.urls')),
    re_path(r'^cron/', include('cron.urls')),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

if settings.URL_PREFIX:
    urlpatterns = [
        path(f'{settings.URL_PREFIX}', include(urlpatterns)),
        re_path(r'^healthcheck/$', views.HealthCheckView.as_view(), name='healthcheck')]
else:
    urlpatterns += [re_path(r'^healthcheck/$', views.HealthCheckView.as_view(), name='healthcheck')]