"""
URL configuration for materia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path

from core.views import main as core_views
from django.conf import settings
from materia_ucfauth.authentication.saml_views import SamlLoginView, SamlLogoutView

urlpatterns = [
    path("", core_views.index, name="home page"),
    path("help/", core_views.help, name="help"),
    path("api/json/user_get", core_views.user_get, name="user_get"),
]

# Register SAML login routes
if getattr(settings, "SAML_ENABLED", False) == True:
    urlpatterns += [
        path("login/", SamlLoginView.as_view(), name="saml_login"),
        path("logout/", SamlLogoutView.as_view(), name="saml_logout"),
        path(r'saml2/', include('materia_ucfauth.authentication.saml_urls')),
    ]
else:
    # Register default login routes
    urlpatterns += [
        path("login/", core_views.LoginView.as_view(), name="login"),
        path("logout/", core_views.LogoutView.as_view(), name="logout"),
    ]

handler404 = "core.views.main.handler404"
handler500 = "core.views.main.handler500"
