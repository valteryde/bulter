
from django.shortcuts import render, HttpResponse

# Create your views here.
def index(request):
	context = {}
	return render(request, 'sign/signin.html', context)

def signup_standard(request):
	context = {}
	return render(request, 'sign/signup.html', context)
