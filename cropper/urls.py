from django.urls import path

from .views import CropImageApiView, CropSingleImageApiView, CropperSetData, CropperSetDataSingle

urlpatterns = (
    path('/crop-images/set-data/<uuid:op_uuid>', CropperSetData.as_view()),
    path('/crop-image/set-data/<uuid:op_uuid>', CropperSetDataSingle.as_view()),
    path('/crop-image/<uuid:op_uuid>', CropSingleImageApiView.as_view()),
    path('/crop-images/<uuid:op_uuid>', CropImageApiView.as_view()),
)