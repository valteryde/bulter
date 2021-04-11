from django.contrib import admin
from .models import User, Event, UserEvent

# Register your models here.
admin.site.register(User)
admin.site.register(Event)
admin.site.register(UserEvent)

admin.site.site_header  =  "Bulter Adminstration"  
admin.site.site_title  =  "Admin"
admin.site.index_title  =  "Butler"
