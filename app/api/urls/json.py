from django.urls import path

# this could probably be handled a bit more neatly
from api.views.widgets import WidgetsApi
from api.views.users import UsersApi
from api.views.sessions import SessionsApi

urlpatterns = [
    path('widgets_get_by_type/', WidgetsApi.by_type),
    path('user_get', UsersApi.get),
    path('session_author_verify/', SessionsApi.author_verify)
]
