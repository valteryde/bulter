
from django.urls import path
from . import views

urlpatterns = [
    path('tunnel/', views.mergeTunnel, name='createUserEvent'),
	path('link/<share>', views.reroute, name='shareLink'),
]
