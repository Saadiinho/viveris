from django.urls import path
from .views import  scan_barcode, bin_managed , user_recycling_activity

urlpatterns = [
    path('scan/', scan_barcode, name='scan_barcode'),
    path('trash/', bin_managed, name='bin_managed'),
    path('activities/', user_recycling_activity, name='user_recycling_activity'),
]
