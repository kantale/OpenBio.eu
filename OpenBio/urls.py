"""OpenBio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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

from django.conf import settings
from django.contrib import admin
from django.urls import path, include


INSTALLED_APPS_URLS = settings.INSTALLED_APPS_URLS if hasattr(settings, 'INSTALLED_APPS_URLS')  else []

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('static.urls')),
    path('platform/', include('app.urls')),
]

for app_url, app_url_file in INSTALLED_APPS_URLS:
   urlpatterns.append(path(app_url, include(app_url_file)))

