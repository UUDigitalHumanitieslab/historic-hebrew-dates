"""historic_hebrew_dates_ui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView

from rest_framework import routers

from .index import index
from .proxy_frontend import proxy_frontend

api_router = routers.DefaultRouter()  # register viewsets with this router

if settings.PROXY_FRONTEND:
    spa_url = url(r'^(?P<path>.*)$', proxy_frontend)
else:
    spa_url = url(r'', index)

urlpatterns = [
    url(r'^admin$', RedirectView.as_view(url='/admin/', permanent=True)),
    url(r'^api$', RedirectView.as_view(url='/api/', permanent=True)),
    url(r'^api-auth$', RedirectView.as_view(url='/api-auth/', permanent=True)),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(api_router.urls)),
    url(r'^api-auth/', include(
        'rest_framework.urls',
        namespace='rest_framework',
    )),
    spa_url,  # catch-all; unknown paths to be handled by a SPA
]
