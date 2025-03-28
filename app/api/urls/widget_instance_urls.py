from api.views.widget_instance_api import WidgetInstanceAPI
from django.urls import path

urlpatterns = [
    path("save/", WidgetInstanceAPI.save),
    path("update/", WidgetInstanceAPI.update),
    path("lock/", WidgetInstanceAPI.widget_instance_lock),
]
