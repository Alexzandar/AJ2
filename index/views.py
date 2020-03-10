from django.http import *
from django.shortcuts import render, render_to_response,redirect
import json
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import datetime
from django.db.models import Q
from django.core.paginator import Paginator

@login_required(login_url='/actionbot/login/')
def index(request):
    return render(request, 'etl/index.html')			

@login_required(login_url='/actionbot/login/')
def clients(request):
	return render(request, 'etl/uac_addclients.html',{ 'erp' :[],'tools' :[]})

