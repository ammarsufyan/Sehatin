from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
# Assigning the function to each url
def index(request):
    return render(request, 'index.html')