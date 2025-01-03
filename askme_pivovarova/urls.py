"""
URL configuration for askme_pivovarova project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf.urls.static import static

from app import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('hot/', views.hot, name='hot'),
    path('answer/<int:id>', views.answer, name='answer'),
    path('ask/', views.ask, name='ask'),
    path('login/', views.login, name='login'),
    path('reg/', views.reg, name='reg'),
    path('settings/', views.settings, name='settings'),
    path('tag/<str:tag_name>', views.tag, name="tag"),
    path('admin/', admin.site.urls),
    path('logout/', views.logout, name="logout")
]
