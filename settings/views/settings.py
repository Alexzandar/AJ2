from django.http import *
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import datetime
from pprint import pprint
from masters.models import Customer

import json
from django.core import serializers


@login_required(login_url='/actionbot/login/')
def schedules(request):	
	clients = Customer.objects.order_by("full_name").all()
	return render(request, 'etl/schedules.html',{'clients':clients})	