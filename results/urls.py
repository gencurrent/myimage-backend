from django.urls import path, re_path

from .views import ResultView

urlpatterns = (
    # path('/<operation>/<operation_uuid>', ResultView.as_view()),
    re_path(r'/(?P<operation>[a-zA-Z0-9\-]*)/(?P<operation_uuid>[a-zA-Z0-9\-]*)', ResultView.as_view()),
)