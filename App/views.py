from django.shortcuts import render,redirect,render_to_response
from django.http import HttpResponse
from django.http import Http404


def index(request):

	return render(request, 'index.html')