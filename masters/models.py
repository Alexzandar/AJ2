from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import datetime

class Erp(models.Model):
    erp_id = models.AutoField(primary_key=True)
    erp_name = models.CharField(max_length=20)
    description = models.CharField(max_length=50)

    class Meta:
        db_table = "bot_erp"

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=40)
    activation_date = models.DateField(null=True)
    description = models.TextField(null=False)
    status= models.CharField(max_length=1,default='Y')
    entry_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User,default=2, on_delete=models.CASCADE)

    class Meta:
        db_table = "bot_customers"

class CustomerSystem(models.Model):
    id = models.AutoField(primary_key=True)
    cust_id = models.ForeignKey(Customer, default=0, on_delete=models.CASCADE, db_column='cust_id')
    erp_id = models.ForeignKey(Erp, default=0, on_delete=models.CASCADE, db_column='erp_id')
    system_name = models.CharField(max_length=50)
    client_code = models.CharField(max_length=10)
    odata_system_url = models.CharField(max_length=100)
    auth_type = models.CharField(max_length=1, default='')
    integration_sys = models.CharField(max_length=50)

    class Meta:
        db_table = "bot_customer_systems"


class oAuth(models.Model):
    id = models.AutoField(primary_key=True)
    cust_system_id = models.ForeignKey(CustomerSystem, default=0, on_delete=models.CASCADE, db_column='cust_system_id')
    token_url = models.CharField(max_length=255)
    headers = models.TextField()
    payload = models.TextField()

    class Meta:
        db_table = "bot_oauth"

class basicAuth(models.Model):
    id = models.AutoField(primary_key=True)
    cust_system_id = models.ForeignKey(CustomerSystem, default=0, on_delete=models.CASCADE, db_column='cust_system_id')
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = "bot_basic_auth"


class TcodeCategory(models.Model):
    id = models.AutoField(primary_key=True)
    cat_name = models.CharField(max_length=100)

    class Meta:
        db_table = "bot_tcode_cat"

@receiver(post_save, sender=Customer)
def create_django_user(sender, instance=None, created=False, **kwargs):
    if created:
        # print("inside client post save..")
        user_objects = get_user_model().objects
        password = user_objects.make_random_password()
        # print(instance.client_name, password)
        user = user_objects.create_user(username=instance.full_name, password=password)
        instance.user = user
        instance.save()

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
