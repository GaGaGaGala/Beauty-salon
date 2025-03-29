from django.shortcuts import render
from django.views.generic import TemplateView


def index(request):
    return render(request, 'catalog-of-services/index.html')

def base(request):
    return render(request, 'base.html')