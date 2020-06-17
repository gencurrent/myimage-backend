from django.urls import path

from .views import CropDataApiView, CropImageApiView

urlpatterns = (
    path('crop-data', CropDataApiView.as_view()),
    path('crop-image', CropImageApiView.as_view()),
)