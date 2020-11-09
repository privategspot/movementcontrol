from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FacilityObject


# Register your models here.
admin.site.register(FacilityObject)
admin.site.register(User, UserAdmin)
