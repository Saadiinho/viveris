from django.urls import path
from .views import  scan_barcode, bin_managed

urlpatterns = [
    path('scan/', scan_barcode, name='scan_barcode'),
    path('trash/', bin_managed, name='bin_managed')
]