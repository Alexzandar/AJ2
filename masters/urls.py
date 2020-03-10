from django.conf.urls import url
from masters.views import erp, clients, tcode_category

urlpatterns = [	

	#ERP
	url(r'^erp/$', erp.master_erp, name='ERP Master'),
    url(r'^erpsave', erp.new_erp, name='ERP Save'),
    url(r'^erpdelete/(?P<id>\d+)', erp.delete_erp, name='ERP Delete'),
    url(r'^erpupdate/', erp.update_erp, name='ERP Update'),

    #Customers
	url(r'^customers/$', clients.master_customers, name='Customer Master'),
	url(r'^save-customer/$', clients.saveCustomer, name='Save Customer'),
	url(r'^customer-delete/(?P<id>\d+)$', clients.delete_customer, name='Customer Delete'),

	#Variant Management
	url(r'^variants/$', clients.variants, name='Variants'),

	#T Codes
	url(r'^t-codes/$', clients.tcodes, name='T Codes'),
	url(r'^t-code/create$', clients.create_tcode, name='Create T Code'),
	url(r'^t-code/get-screen-fields$', clients.getScreenFields, name='Get Screen Fields'),

	#Log
	url(r'^logs/$', clients.logs, name='logs'),
	url(r'^results/$', clients.logresults, name='Load File content'),
	url(r'^logfiles/$', clients.logfiles, name='Load File List'),

	#TCode Categories
	url(r'^t-code-category/$', tcode_category.categories, name='TCode Categories'),
	url(r'^save-category/$', tcode_category.saveCategory, name='Save TCode Category'),
	url(r'^category-delete/(?P<id>\d+)$', tcode_category.deleteCategory, name='Delete TCode Category'),
	
]
