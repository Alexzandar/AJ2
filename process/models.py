from django.db import models
from masters.models import Customer

# Create your models here.
class TaskSchedule(models.Model):
    id = models.AutoField(primary_key=True)
    cust_id = models.ForeignKey(Customer,default=2, on_delete=models.CASCADE)
    task_id = models.TextField(null=False)
    bot_id = models.TextField(null=False)
    status = models.TextField(max_length=1, null=False)
    entry_date = models.DateField(null=True)

    class Meta:
        db_table = "bot_task_schedule"
