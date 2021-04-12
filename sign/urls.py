
from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('up/', views.signup_standard, name='createUser_standard'),
]
