from django.urls import path

from . import views

urlpatterns = [
	path('', views.index),
	path('register/', views.register), # Register a new user 
	path('login/', views.login), # Login a user
	path('logout/', views.logout), # Logout a user
	path('reset_password_email/', views.reset_password_email), # Reset password email
]