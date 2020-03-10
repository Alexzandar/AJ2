import os;

from django.http import *
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from masters.models import Customer, Erp, TcodeCategory
from django.db.models import Q
import datetime
from pprint import pprint
from django.contrib.staticfiles.storage import staticfiles_storage
import json
from django.core import serializers
from django.conf import settings
from django.utils.html import strip_tags

@login_required(login_url='/actionbot/login/')
def master_customers(request):
	try:
		query = request.GET['search']
	except Exception as e:
		query = ''
	if query:
		clientdata = Customer.objects.filter(Q(full_name__contains=request.GET['search']) | Q(description__contains=request.GET['search']))
	else: 
		clientdata = Customer.objects.all()		
	page = request.GET.get('page', 1)
	paginator = Paginator(clientdata, 5)
	
	try:
		client = paginator.page(page)
	except PageNotAnInteger:
		client = paginator.page(1)
	except EmptyPage:
		client = paginator.page(paginator.num_pages)
	erps = Erp.objects.all()
	erpData = []
	for erp in erps:
		erpData.append({
			'id':erp.erp_id,
			'text':erp.erp_name
		})

	
	return render(request, 'etl/customers.html', {'data':clientdata, 'clients': client, 'query': query,'erps': json.dumps(erpData)})	

@login_required(login_url='/actionbot/login/')
def saveCustomer(request):
	
	json_data = request.body
	data = json.loads(json_data)
	msg=''
	cid=''
	status ='400'
	customerData = data['customer']
	client_id = customerData['customerId']	
	client_name = data['name']	
	description = data['cust_desc']	
	status = 'Y'
	# status = data['customerStatus']
	customer_activation_date =  datetime.datetime.strptime(data['activation_date'], '%m/%d/%Y') if data['activation_date'] else None
	try:
		# Decides whether to create an object or edit an existing object
		if(client_id):
			client = Customer.objects.get(id=client_id)
			if(client):
				client.full_name = client_name
				client.description = description
				client.status = status
				client.user = request.user
				if(customer_activation_date):
					client.activation_date = customer_activation_date
				client.save()
				msg ='Records has been Updated !'			
				status='200'
			else:
				msg = "Something went wrong."
				status = '400'
		else:
			data=Customer(
			full_name  = client_name,
			description  = description,
			status = status,
			user = request.user,
			activation_date = customer_activation_date
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
def delete_customer(request, id):
	Customer.objects.filter(id=id).delete()	
	return redirect('/actionbot/masters/customers')

@login_required(login_url='/actionbot/login/')	
def variants(request):
	clientdata = Customer.objects.all()
	return render(request, 'etl/variants.html', {'customers': clientdata})	

@login_required(login_url='/actionbot/login/')
def tcodes(request):
	t_codes = ['KE5Z', 'KKAI', 'KKAJ', 'CJI5', 'KE5B',
      'F13E', 'F.13', 'FAGLF101', 'FAGL_FCV', 'AFBP', 'AFAB', 'CJI3'
    ]
	with open(settings.BASE_DIR+'/static/etl/data/screen_fields.json') as json_file:
		data = json.load(json_file)	
		# data2 = {'test' : data['Fixed Asset']['KE5Z']}

		return render(request, 'etl/tcodes.html',{'data':data, 't_codes': t_codes})	

@login_required(login_url='/actionbot/login/')
def create_tcode(request):	
	erps = Erp.objects.all()
	categories = TcodeCategory.objects.all()
	return render(request, 'etl/tcode_create.html', {'erps': erps, 'categories': categories})	

@login_required(login_url='/actionbot/login/')
def getScreenFields(request):	
	erps = Erp.objects.all()
	categories = TcodeCategory.objects.all()
	return render(request, 'etl/tcode_create.html', {'erps': erps, 'categories': categories})	

@login_required(login_url='/actionbot/login/')
def logresults(request):
	json_data = request.GET.get('formdata')
	data = json.loads(json_data)
	fname = data['fName']
	status = '200'
	msg=''

	file_content=''
	try:
		#flie_list = os.listdir(PROJECT_PATH+'\outfiles')
		f = open('outfiles/'+fname, 'r')
		file_content = f.read()
		f.close()
	except Exception as e:
		status = '400'
		msg = str(e)
	finally:
		js = {'f_content':file_content,'status':status,'msg':msg}
		return JsonResponse(js)


@login_required(login_url='/actionbot/login/')
def logfiles(request):
	status = '200'
	try:
		PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))
		flie_list = os.listdir(PROJECT_PATH+'\outfiles')
	except Exception as e:
		status = '400'
	finally:
		js = {'status':status,'file_list':flie_list}
		return JsonResponse(js)

@login_required(login_url='/actionbot/login/')
def logs(request):
	return render(request, 'etl/results.html')