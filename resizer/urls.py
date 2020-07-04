from django.urls import path

from .views import ResizerSetDataSingle, ResizeManyImagesApiView

urlpatterns = (
    path('/set-data/<uuid:op_uuid>', ResizerSetDataSingle.as_view()),
    # path('/resize-image/<uuid:crop_uuid>', ResizeSingleImageApiView.as_view()),
    path('/resize-images/<uuid:op_uuid>', ResizeManyImagesApiView.as_view()),
)