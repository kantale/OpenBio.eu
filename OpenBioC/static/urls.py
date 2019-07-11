from django.urls import path, re_path

from . import views

urlpatterns = [
	path('', views.static_en),
	path('gr/', views.static_gr),
]


