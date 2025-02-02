from django.urls import path
from .views import ServeWasteImageView, WasteClassificationView

urlpatterns = [
    path('classify/', WasteClassificationView.as_view(), name='waste-classification'),
    path('waste_classifications/<str:filename>', ServeWasteImageView.as_view(), name='serve-waste-image')
]