"""icrawler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^get_posts_by_country', views.get_posts_by_country),
    url(r'^get_dailypost_by_tag', views.get_dailypost_by_tag),
    url(r'^get_hype_by_tag', views.get_hype_by_tag),
    url(r'^crawl', views.get_hype_by_tag),
]

# handler403 = 'views.status_403'
# handler404 = 'views.status_404'
# handler500 = 'views.status_500'