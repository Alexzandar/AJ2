from django.db import models
from django.contrib.auth.models import User
from masters.models import Customer,TcodeCategory,CustomerSystem

# Create your models here.
class CadencySetting(models.Model):
    id = models.AutoField(primary_key=True)
    cust_id = models.ForeignKey(Customer,default=1, on_delete=models.CASCADE, db_column='cust_id')
    cadency_system_url = models.TextField(null=False)
    subscription_key = models.CharField(max_length=20)
    host = models.CharField(max_length=250)
    content_type= models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bot_cadency_settings"

class Library(models.Model):
    id = models.AutoField(primary_key=True)
    tcode = models.CharField(max_length=50)
    program_name = models.CharField(max_length=50)
    tcode_cat = models.ForeignKey(TcodeCategory,default=1, on_delete=models.CASCADE, db_column='tcode_cat')
    tcode_name = models.CharField(max_length=20)
    variant_name = models.CharField(max_length=20)
    variant_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bot_library"

class VariantMaster(models.Model):
    id = models.AutoField(primary_key=True)
    cust_id = models.ForeignKey(Customer,default=1, on_delete=models.CASCADE, db_column='cust_id')
    cust_system_id = models.ForeignKey(CustomerSystem,default=1, on_delete=models.CASCADE, db_column='cust_system_id')
    tcode = models.CharField(max_length=50)
    bot_id = models.CharField(max_length=50)
    program_name = models.CharField(max_length=50)
    variant_name = models.CharField(max_length=20)
    description = models.TextField()
    status = models.CharField(max_length=20)
    output_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bot_variant_master"

class VariantDetail(models.Model):
    id = models.AutoField(primary_key=True)
    v_master_id = models.ForeignKey(VariantMaster,default=1, on_delete=models.CASCADE, db_column='v_master_id')
    name = models.CharField(max_length=20)
    v_type = models.CharField(max_length=20)
    v_option = models.CharField(max_length=20)
    v_sign = models.CharField(max_length=20)
    low = models.CharField(max_length=100)
    high = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bot_variant_details"

