import os;

from django.http import *
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from masters.models import Customer,Erp, TcodeCategory
from django.db.models import Q
import datetime
from pprint import pprint
from django.contrib.staticfiles.storage import staticfiles_storage
import json
from django.core import serializers
from django.conf import settings

@login_required(login_url='/actionbot/login/')
def categories(request):
	try:
		query = request.GET['search']
	except Exception as e:
		query = ''
	if query:
		categories = TcodeCategory.objects.filter(Q(cat_name__contains=request.GET['search']))
	else: 
		categories = TcodeCategory.objects.all()		
	page = request.GET.get('page', 1)
	paginator = Paginator(categories, 5)
	
	try:
		categories = paginator.page(page)
	except PageNotAnInteger:
		categories = paginator.page(1)
	except EmptyPage:
		categories = paginator.page(paginator.num_pages)

	
	return render(request, 'etl/tcode_categories.html', {'categories': categories})	

@login_required(login_url='/actionbot/login/')
def saveCategory(request):
	msg=''
	cid=''
	status ='400'
	cat_id = request.POST.get('categoryId')	
	cat_name = request.POST.get('categoryName')
	try:
		# Decides whether to create an object or edit an existing object
		if(cat_id):
			category = TcodeCategory.objects.get(id=cat_id)
			if(category):
				category.cat_name = cat_name
				category.save()
				msg ='Records has been Updated !'			
				status='200'
			else:
				msg = "Something went wrong."
				status = '400'
		else:
			data=TcodeCategory(
			cat_name  = cat_name
			)
			data.save()					
			msg ='Records has been Saved !'			
			status='200'
	except Exception as e:
		msg = "Error Occurred: " + str(e)
		status = '400'
	finally:	
		js = {'message':msg,'status':status}
		return JsonResponse(js)

@login_required(login_url='/actionbot/login/')	
def deleteCategory(request, id):
	# Check if category is not using in t_code library and detail table
	# TODO
	TcodeCategory.objects.filter(id=id).delete()	
	return redirect('/actionbot/masters/t-code-category')