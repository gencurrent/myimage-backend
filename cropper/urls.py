from django.urls import path

from .views import CropDataApiView, CropImageApiView, CropSingleImageApiView, CropperSetData, CropperSetDataSingle

urlpatterns = (
    path('/crop-data', CropDataApiView.as_view()),
    path('/set-data', CropperSetData.as_view()),
    path('/set-data/<uuid:crop_uuid>', CropperSetDataSingle.as_view()),
    path('/crop-image/<uuid:crop_uuid>', CropSingleImageApiView.as_view()),
    path('/crop-images', CropImageApiView.as_view()),
)