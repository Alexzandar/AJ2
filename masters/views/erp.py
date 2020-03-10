from django.http import *
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from masters.models import Erp
from django.db.models import Q

#### #### MASTERS ###############
##  ERP ####
@login_required(login_url='/actionbot/login/')
def master_erp(request):
	try:
		query = request.GET['search']
	except Exception as e:
		query = ''
	if query:
		erpdata = Erp.objects.filter(Q(erp_name__contains=query) | Q(description__contains=query))
	else: 
		erpdata = Erp.objects.all().order_by('-erp_id') 
	page = request.GET.get('page', 1)
	paginator = Paginator(erpdata, 15)
	
	try:
		erp = paginator.page(page)
	except PageNotAnInteger:
		erp = paginator.page(1)
	except EmptyPage:
		erp = paginator.page(paginator.num_pages)
		
	return render(request, 'etl/erp.html', {'erps': erp})	

def new_erp(request):
    input = Erp(erp_name=request.POST['erpname'], description=request.POST['erpdesc'])
    input.save()
    return redirect('/actionbot/masters/erp')
	
def delete_erp(request, id):
    data = Erp.objects.get(erp_id=id)
    data.delete()
    return redirect('/actionbot/masters/erp')
	
def update_erp(request):

	 data = Erp.objects.get(erp_id=request.POST['erpid'])
	 data.erp_name = request.POST['editerpname']
	 data.description = request.POST['editerpdesc']
	 data.save()
	 return redirect('/actionbot/masters/erp')
