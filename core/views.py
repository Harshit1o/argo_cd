from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello from Django + ArgoCD 🚀")

# Create your views here.
