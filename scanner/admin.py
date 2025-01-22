from django.contrib import admin
from scanner import models
# Register your models here.
admin.site.register(models.Product)
admin.site.register(models.Bin)
admin.site.register(models.RecyclingActivity)

