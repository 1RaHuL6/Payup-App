from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Define the index view
def index(request):
    return render(request, 'register/index.html')
