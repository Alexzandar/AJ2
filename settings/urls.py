from django.conf.urls import url
from settings.views import settings

urlpatterns = [	
url(r'^schedule/$', settings.schedules, name='Schedule'),
]
